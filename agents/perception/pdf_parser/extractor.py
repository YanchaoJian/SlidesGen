import os
import json
import time
import logging
import re
from typing import List, Optional

import torch
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.schema import BlockTypes
from openai import OpenAI
from surya.settings import settings

from agents.pdf_parser.image_orientation import fix_image_orientation


class ContentExtractor:
    def __init__(self, pdf_path: str, marker_path: str, output_dir: str = "output", device: Optional[str] = None):
        """
        初始化内容提取器。

        Args:
            pdf_path (str): 输入的 PDF 文件路径。
            marker_path (str): 本地 Marker 模型目录。
            output_dir (str): 输出目录。
            device (Optional[str]): 指定计算设备 ('cuda' or 'cpu')。如果为 None，则自动检测。
        """
        self.pdf_path = pdf_path
        self.marker_path = marker_path
        self.output_dir = output_dir

        # 准备会话特定的输出目录
        self.img_dir = os.path.join(self.output_dir, "images")
        self.raw_dir = os.path.join(self.output_dir, "raw")
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # --- GPU/CPU 设备自动检测 ---
        if device:
            self.device = device
        else:
            # 检查是否有可用 GPU，优先使用 GPU 1
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                if gpu_count > 1:
                    self.device = "cuda:1"  # 指定使用第二块 GPU
                    self.logger.debug(f"Multiple GPUs detected ({gpu_count}).")
                else:
                    self.device = "cuda"  # 只有一块 GPU，使用默认的 GPU 0
            else:
                self.device = "cpu"

        self.logger.info(f"Marker will use device: '{self.device}'")

        # 设置 Marker 模型路径 (如果需要)
        self._setup_marker_models()

    def _setup_marker_models(self):
        """
        配置模型路径，将 s3:// 路径映射到本地目录。

        surya 的默认路径格式为 "s3://layout/2025_02_18"，
        本地模型目录结构为 models/marker/layout/2025_02_18/。
        映射策略：将 "s3://" 替换为本地 model_root + "/"。
        """
        model_root = os.path.abspath(self.marker_path)

        for checkpoint in [
            "LAYOUT_MODEL_CHECKPOINT",
            "DETECTOR_MODEL_CHECKPOINT",
            "OCR_ERROR_MODEL_CHECKPOINT",
            "TABLE_REC_MODEL_CHECKPOINT",
            "RECOGNITION_MODEL_CHECKPOINT",
            "INLINE_MATH_MODEL_CHECKPOINT",
            "TEXIFY_MODEL_CHECKPOINT",
        ]:
            if not hasattr(settings, checkpoint):
                continue
            value = getattr(settings, checkpoint)
            if isinstance(value, str) and value.startswith("s3://"):
                # s3://layout/2025_02_18 -> models/marker/layout/2025_02_18
                relative_path = value.replace("s3://", "")
                local_path = os.path.join(model_root, relative_path)
                if os.path.isdir(local_path):
                    setattr(settings, checkpoint, local_path)
                    self.logger.debug(f"Set {checkpoint} -> {local_path}")
                else:
                    self.logger.warning(f"Local model not found for {checkpoint}: {local_path}")

    def extract_content(self, openai_client: Optional[OpenAI] = None, model_name: str = "gpt-4o"):
        """
        使用 Marker 从 PDF 中提取 Markdown、图片、表格和公式。
        Marker 可直接识别表格和公式，无需 LLM 增强。

        Args:
            openai_client: OpenAI 客户端，用于图片方向检测。为 None 时跳过方向修正。
            model_name: 多模态模型名称，用于图片方向检测。
        """
        try:
            self.logger.info(f"Starting content extraction for: {self.pdf_path}")

            # 1. 加载 Marker 模型到指定设备 (GPU/CPU)
            model_lst = create_model_dict(device=self.device)
            converter = PdfConverter(artifact_dict=model_lst)

            # 2. 构建 Document 对象（用于块级导航获取公式上下文），然后渲染
            start_time = time.time()
            document = converter.build_document(self.pdf_path)
            renderer = converter.resolve_dependencies(converter.renderer)
            rendered_output = renderer(document)
            duration = time.time() - start_time
            self.logger.info(f"PDF conversion finished in {duration:.2f} seconds.")

            # 3. 从转换结果中提取文本和图片 (使用稳定的 API)
            markdown_text, _, images = text_from_rendered(rendered_output)

            # 4. 保存提取出的图片，并构建图片信息列表
            #    如果提供了 OpenAI 客户端，先用多模态模型检测并修正图片方向
            image_list = []
            for filename, image_obj in images.items():
                if openai_client is not None:
                    image_obj = fix_image_orientation(image_obj, openai_client, model=model_name)

                image_filepath = os.path.join(self.img_dir, filename)
                image_obj.save(image_filepath, "JPEG")

                caption = self._extract_image_caption(markdown_text, filename)

                image_info = {
                    "caption": caption,
                    "path": image_filepath
                }
                image_list.append(image_info)

            # 5. 提取表格（从 Markdown）和公式（从 Document 块级导航获取上下文）
            tables = self._extract_tables_from_markdown(markdown_text)
            equations = self._extract_equations_from_document(document)

            self.logger.info(f"Extracted {len(tables)} tables and {len(equations)} equations from Marker output.")

            # 6. 组装最终输出
            content = {
                "full_text": markdown_text,
                "images": image_list,
                "tables": tables,
                "equations": equations,
            }

            self.logger.debug(f"Content extraction successful: Text length={len(markdown_text)}, "
                            f"Images={len(image_list)}, Tables={len(tables)}, Equations={len(equations)}")
            return content

        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}", exc_info=True)
            return None

    def _extract_tables_from_markdown(self, markdown_text: str) -> List[dict]:
        """
        从 Marker 生成的 Markdown 中提取所有表格。
        Marker 会将 PDF 中的表格转换为标准 Markdown 表格语法。

        返回格式与下游 planner 兼容:
            [{"caption": "...", "markdown": "..."}, ...]
        """
        tables = []
        lines = markdown_text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # 检测表格起始行：包含 | 分隔符的行
            if '|' in line and self._is_table_row(line):
                table_lines = []
                caption = ""

                # 向上查找表格标题 (Table X: ... 或 表 X: ...)
                for j in range(max(0, i - 5), i):
                    cap_match = re.search(
                        r'(?:Table|表)\s*(\d+)[:\.\s]*(.*)',
                        lines[j], re.IGNORECASE
                    )
                    if cap_match:
                        caption = lines[j].strip().lstrip('#').strip()
                        break

                # 收集连续的表格行
                while i < len(lines) and self._is_table_row(lines[i].strip()):
                    table_lines.append(lines[i])
                    i += 1

                # 如果没找到上方标题，尝试在表格下方查找
                if not caption:
                    for j in range(i, min(len(lines), i + 3)):
                        cap_match = re.search(
                            r'(?:Table|表)\s*(\d+)[:\.\s]*(.*)',
                            lines[j], re.IGNORECASE
                        )
                        if cap_match:
                            caption = lines[j].strip().lstrip('#').strip()
                            break

                table_markdown = '\n'.join(table_lines)

                # 至少包含分隔行（|---|---|）才算有效表格
                if any(re.match(r'\s*\|[\s\-:|]+\|', tl) for tl in table_lines):
                    tables.append({
                        "caption": caption if caption else f"Table {len(tables) + 1}",
                        "markdown": table_markdown,
                    })
            else:
                i += 1

        return tables

    @staticmethod
    def _is_table_row(line: str) -> bool:
        """判断一行是否为 Markdown 表格行（包含 | 且非图片引用）。"""
        stripped = line.strip()
        if not stripped:
            return False
        # 排除图片引用行 ![...](...) 和标题行
        if stripped.startswith('!') or stripped.startswith('#'):
            return False
        # 必须包含 | 且以 | 开头或结尾
        if '|' not in stripped:
            return False
        # 表格行应以 | 开头
        return stripped.startswith('|')

    def _extract_equations_from_document(self, document) -> List[dict]:
        """
        从 Marker Document 对象中提取公式块，并利用块级导航 API
        获取每个公式前后各一个块的文本作为上下文。

        返回格式:
            [{"latex": "...", "context": "..."}, ...]
        """
        equations = []
        seen = set()

        for page in document.pages:
            if not page.structure:
                continue
            for block_id in page.structure:
                block = document.get_block(block_id)
                if block is None or block.block_type != BlockTypes.Equation:
                    continue

                # 获取公式 LaTeX 内容
                latex = block.raw_text(document).strip()
                if not latex or latex in seen or len(latex) <= 3:
                    continue
                seen.add(latex)

                # 通过 Document 导航 API 获取前后块文本，拼接为公式上下文
                parts = []

                prev_block = document.get_prev_block(block)
                if prev_block is not None:
                    text = prev_block.raw_text(document).strip()
                    if text:
                        parts.append(text)

                parts.append(latex)

                next_block = document.get_next_block(block)
                if next_block is not None:
                    text = next_block.raw_text(document).strip()
                    if text:
                        parts.append(text)

                equations.append({
                    "latex": latex,
                    "context": "\n".join(parts),
                })

        return equations

    def _extract_image_caption(self, markdown_text: str, image_filename: str) -> str:
        """从 Markdown 文本中为图片智能查找标题。"""
        try:
            # 优先匹配 Markdown 格式: ![caption](path/to/image.jpg)
            pattern = rf'!\[(.*?)\]\([^)]*{re.escape(image_filename)}[^)]*\)'
            matches = re.findall(pattern, markdown_text)
            if matches and matches[0].strip():
                return matches[0].strip()

            # 备用逻辑：查找图片附近 "Figure X:" 或 "Fig. X:" 格式的文本
            lines = markdown_text.split('\n')
            for i, line in enumerate(lines):
                if image_filename in line:
                    # 优先查找图片下方的Figure标题（1-5行内）
                    for j in range(i+1, min(len(lines), i+6)):
                        figure_match = re.search(r'(?:Figure?|Fig\.?)\s*(\d+)[:\.]?\s*(.*)', lines[j], re.IGNORECASE)
                        if figure_match:
                            caption_text = figure_match.group(2).strip()
                            if caption_text:
                                return caption_text

                    # 如果下方没找到，再查找上方的Figure标题（1-3行内）
                    for j in range(max(0, i-3), i):
                        figure_match = re.search(r'(?:Figure?|Fig\.?)\s*(\d+)[:\.]?\s*(.*)', lines[j], re.IGNORECASE)
                        if figure_match:
                            caption_text = figure_match.group(2).strip()
                            if caption_text:
                                return caption_text

                    # 如果还是没找到，尝试查找图片后面紧跟的非空行作为caption
                    for j in range(i+1, min(len(lines), i+4)):
                        line_text = lines[j].strip()
                        if (line_text and
                            not line_text.startswith('!') and
                            not re.match(r'^\d+$', line_text) and
                            not re.match(r'^[#*-]+$', line_text) and
                            len(line_text) > 10):
                            return line_text
            return ""

        except Exception as e:
            self.logger.warning(f"Error while extracting caption for {image_filename}: {e}")
            return ""

    def save_content(self, content: dict, output_file: Optional[str] = None) -> str:
        """将提取的内容保存为 JSON 文件。"""
        if output_file is None:
            output_file = os.path.join(self.raw_dir, "pdf-content.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Raw content saved for debugging at: {output_file}")
        return output_file

# ==============================================================================
# 便捷函数 (用于在 LangGraph Node 中调用)
# ==============================================================================
def extract_pdf(pdf_path: str, marker_path: str, output_dir: str,
                api_key: Optional[str] = None, base_url: Optional[str] = None,
                model_name: str = "gpt-4o") -> tuple:
    """
    顶层便捷函数，实例化 ContentExtractor 并执行提取。
    现在直接提取文字、图片、表格和公式，无需后续 LLM 增强。

    Args:
        pdf_path: PDF 文件路径。
        marker_path: Marker 模型目录。
        output_dir: 输出目录。
        api_key: OpenAI API Key，用于图片方向检测。为 None 时跳过。
        base_url: OpenAI API Base URL。
        model_name: 多模态模型名称。
    """
    try:
        extractor = ContentExtractor(pdf_path, marker_path, output_dir)

        openai_client = None
        if api_key:
            openai_client = OpenAI(api_key=api_key, base_url=base_url)

        content = extractor.extract_content(openai_client=openai_client, model_name=model_name)

        if content:
            output_file = extractor.save_content(content)
            return content, output_file, extractor.img_dir
    except Exception as e:
         logging.error(f"Top-level extract_content failed: {e}", exc_info=True)

    return None, None, None