import os
import json
import time
import logging
import re
from typing import Optional

import torch
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from surya.settings import settings


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
        """配置模型缓存路径。"""
        model_root = self.marker_path
        settings.MODEL_CACHE_DIR = model_root
        # 这个循环逻辑在新版中可能不是必须的，但保留以确保向后兼容性
        for checkpoint in [
            "LAYOUT_MODEL_CHECKPOINT", 
            "DETECTOR_MODEL_CHECKPOINT", 
            "OCR_ERROR_MODEL_CHECKPOINT", 
            "TABLE_REC_MODEL_CHECKPOINT",
            "RECOGNITION_MODEL_CHECKPOINT",
        ]:
            if hasattr(settings, checkpoint):
                value = getattr(settings, checkpoint)
                if isinstance(value, str) and "s3://" in value:
                    value = value.replace("s3://", "/")
                    setattr(settings, checkpoint, model_root + value)

    def extract_content(self):
        """
        使用 Marker 从 PDF 中提取高质量 Markdown 和图片。
        """
        try:
            self.logger.info(f"Starting content extraction for: {self.pdf_path}")
            
            # 1. 加载 Marker 模型到指定设备 (GPU/CPU)
            model_lst = create_model_dict(device=self.device)
            converter = PdfConverter(artifact_dict=model_lst)
            
            # 2. 转换 PDF
            start_time = time.time()
            rendered_output = converter(self.pdf_path)
            duration = time.time() - start_time
            self.logger.info(f"PDF conversion finished in {duration:.2f} seconds.")
            
            # 3. 从转换结果中提取文本和图片 (使用稳定的 API)
            markdown_text, _, images = text_from_rendered(rendered_output)
            
            # 4. 保存提取出的图片，并构建图片信息列表
            image_list = []
            for filename, image_obj in images.items():
                image_filepath = os.path.join(self.img_dir, filename)
                image_obj.save(image_filepath, "JPEG")
                
                caption = self._extract_image_caption(markdown_text, filename)
                
                image_info = {
                    "caption": caption,
                    "path": image_filepath
                    
                }
                image_list.append(image_info)
            
            # 5. 组装最终输出，格式保持不变
            content = {
                "full_text": markdown_text,
                "images": image_list,
            }
            
            self.logger.debug(f"Content extraction successful: Text length={len(markdown_text)}, Images found={len(image_list)}")
            return content
            
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}", exc_info=True)
            return None
        
    def _extract_image_caption(self, markdown_text: str, image_filename: str) -> str:
    
        """从 Markdown 文本中为图片智能查找标题 (此函数逻辑不变)。"""
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
                        # 扩展正则表达式以匹配更多格式
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
                        # 排除空行、Markdown图片引用行、纯数字行等
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
        """将提取的内容保存为 JSON 文件 (此函数逻辑不变)。"""
        if output_file is None:
            output_file = os.path.join(self.raw_dir, "base_content.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Raw content saved for debugging at: {output_file}")
        return output_file

# ==============================================================================
# 便捷函数 (用于在 LangGraph Node 中调用)
# ==============================================================================
def extract_content(pdf_path: str, marker_path: str, output_dir: str) -> tuple:
    """
    顶层便捷函数，实例化 ContentExtractor 并执行提取。
    """
    try:
        # 自动检测 GPU
        extractor = ContentExtractor(pdf_path, marker_path, output_dir)
        base_content = extractor.extract_content()
    
        if base_content:
            output_file = extractor.save_content(base_content)
            return base_content, output_file, extractor.img_dir
    except Exception as e:
         logging.error(f"Top-level extract_content failed: {e}", exc_info=True)
    
    return None, None, None