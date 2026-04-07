import json
import os
import logging
import tempfile
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agents.execution.prompts import VISUAL_CRITIQUE_SYSTEM_PROMPT, VISUAL_CRITIQUE_USER_PROMPT
from pipeline.pptx_merger import merge_svgs_to_pptx
from utils.pptx_imaging import pptx_to_images
from utils.llm import LLMConfig, create_llm, encode_image_to_base64, parse_json_response, raise_if_fatal_llm_error

logger = logging.getLogger(__name__)


def evaluate_and_critique_slide(
    slide_code: str,
    svg_path: str,
    slide_style_protocol: str,
    llm_config: LLMConfig,
) -> Optional[str]:
    """
    对单张幻灯片进行视觉评估，并生成可操作的修改建议。

    流程: SVG 文件 → 临时 PPTX → 截图 → 多模态 LLM 审查

    Args:
        slide_code: 生成该幻灯片的 SVG 源码。
        svg_path: 已 finalize 的 SVG 文件路径。
        slide_style_protocol: 自然语言形式的主题风格描述。
        llm_config: LLM 连接配置。

    Returns:
        如果发现问题，返回一个包含修改建议的字符串；如果质量合格，返回 None。
    """
    if not svg_path or not os.path.exists(svg_path):
        logger.error(f"❌ Critique failed: SVG file not found at {svg_path}")
        return "SVG file not found."

    logger.info(f"🧐 Visual Critic is evaluating slide: {os.path.basename(svg_path)}...")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 1. SVG → 临时 PPTX
            temp_pptx = os.path.join(temp_dir, "preview.pptx")
            result = merge_svgs_to_pptx([svg_path], temp_pptx)
            if not result:
                logger.warning("   -> ⚠️ Failed to convert SVG to PPTX for preview.")
                return "Failed to convert SVG to PPTX for visual evaluation."

            # 2. PPTX → 截图
            logger.info("   -> Converting slide to image for review...")
            image_files = pptx_to_images(temp_pptx, temp_dir, dpi=300)
            if not image_files:
                logger.warning("   -> ⚠️ PPTX to image conversion resulted in 0 images.")
                return "Failed to render slide image for evaluation."

            image_path = image_files[0]
            base64_image = encode_image_to_base64(image_path)

        except Exception as e:
            logger.error(f"   -> ❌ Failed to generate preview image for critique: {e}")
            return f"Internal error during image conversion: {e}"

        # 3. 初始化 Vision LLM
        llm = create_llm(llm_config, temperature=0.1)

        # 4. 构建 Prompt (传入 SVG 源码)
        user_prompt = VISUAL_CRITIQUE_USER_PROMPT.format(
            svg_source=slide_code
        )

        messages = [
            SystemMessage(content=VISUAL_CRITIQUE_SYSTEM_PROMPT),
            HumanMessage(content=[
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ])
        ]

        # 5. 调用 LLM 并获取反馈
        try:
            logger.info(f"   -> Invoking Vision LLM for critique...")
            response = llm.invoke(messages)
            response_content = response.content.strip()

            critique_data = parse_json_response(response_content)
            if critique_data is None:
                return f"CRITICAL FORMAT ERROR: LLM did not return valid JSON. Raw response: {response_content}"

            pass_status = critique_data.get("pass")
            critique_text = critique_data.get("critique", "No critique text provided by the model.")

            critique_item = {
                "pass": pass_status,
                "critique": critique_text,
            }
            # 保存到本地 JSON 列表
            critique_file = svg_path.replace(".svg", "_critique.json")
            append_critique_to_file(critique_item, filepath=critique_file)

            if pass_status is True:
                logger.info(f"   -> ✅ Critique Result: PASS.")
                return None
            elif pass_status is False:
                logger.warning(f"   -> ⚠️ Critique Result: REVISE.")
                return critique_text
            else:
                error_msg = f"Invalid 'pass' value in LLM's JSON response (expected boolean, got {type(pass_status)}). Treating as failure."
                logger.error(f"   -> ❌ {error_msg}")
                return f"INVALID RESPONSE FORMAT: {error_msg} | Critique: {critique_text}"

        except Exception as e:
            raise_if_fatal_llm_error(e)
            logger.error(f"❌ LLM call for critique failed: {e}", exc_info=True)
            return f"LLM evaluation failed unexpectedly: {str(e)}"


def append_critique_to_file(critique_item: dict, filepath: str):
    """将单条审查结果追加保存到本地 JSON 列表文件。"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    else:
        data = []
    data.append(critique_item)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
