import json
import os
import logging
import tempfile
from typing import Optional, Dict, Any

from langchain_core.messages import SystemMessage, HumanMessage

from agent.evaluator.prompts import VISUAL_CRITIQUE_SYSTEM_PROMPT, VISUAL_CRITIQUE_USER_PROMPT
from utils.image_utils import pptx_to_images
from utils.llm_helpers import LLMConfig, create_llm, encode_image_to_base64, extract_json_from_response

logger = logging.getLogger(__name__)

def evaluate_and_critique_slide(
    slide_code: str,
    pptx_path: str,
    slide_style_protocol: str,
    llm_config: LLMConfig,
) -> Optional[str]:
    """
    对单张幻灯片进行视觉评估，并生成可操作的修改建议。

    Args:
        slide_code: 生成该幻灯片的 Python 代码。
        pptx_path: 单页 PPTX 文件的路径。
        slide_style_protocol: 自然语言形式的主题风格描述。
        llm_config: LLM 连接配置。

    Returns:
        如果发现问题，返回一个包含修改建议的字符串；如果质量合格，返回 None。
    """
    if not os.path.exists(pptx_path):
        logger.error(f"❌ Critique failed: PPTX file not found at {pptx_path}")
        return "File not found."
        
    logger.info(f"🧐 Visual Critic is evaluating slide: {os.path.basename(pptx_path)}...")

    # 使用临时目录来存放转换后的图片
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 1. 将单页 PPTX 转换为图片
            logger.info("   -> Converting slide to image for review...")
            image_count = pptx_to_images(pptx_path, temp_dir, dpi=150)
            if image_count == 0:
                logger.warning("   -> ⚠️ PPTX to image conversion resulted in 0 images.")
                return "Failed to render slide image for evaluation."
            
            image_path = os.path.join(temp_dir, "slide_001.jpg") # 假设总是第一张
            base64_image = encode_image_to_base64(image_path)

        except Exception as e:
            logger.error(f"   -> ❌ Failed to convert PPTX to image for critique: {e}")
            return f"Internal error during image conversion: {e}"

        # 2. 初始化 Vision LLM
        llm = create_llm(llm_config, temperature=0.1)

        # 3. 构建 Prompt (传入代码)
        user_prompt = VISUAL_CRITIQUE_USER_PROMPT.format(
            python_script=slide_code
        )

        messages = [
            SystemMessage(content=VISUAL_CRITIQUE_SYSTEM_PROMPT),
            HumanMessage(content=[
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ])
        ]

        # 4. 调用 LLM 并获取反馈
        try:
            logger.info(f"   -> Invoking Vision LLM for critique...")
            response = llm.invoke(messages)
            response_content = response.content.strip()

            # --- 从字符串解析 JSON ---
            critique_data = extract_json_from_response(response_content)
            if critique_data is None:
                return f"CRITICAL FORMAT ERROR: LLM did not return valid JSON. Raw response: {response_content}"

            # 安全地从解析后的字典中获取字段
            pass_status = critique_data.get("pass")
            critique_text = critique_data.get("critique", "No critique text provided by the model.")

            # 4. 根据 'pass' 字段的布尔值进行逻辑判断
            critique_item = {
                "pass": pass_status,
                "critique": critique_text,
            }
            # 新增：保存到本地 JSON 列表
            file_path = pptx_path.replace(".pptx", "_critique.json")
            append_critique_to_file(
                critique_item,
                filepath=file_path
            )

            if pass_status is True:
                logger.info(f"   -> ✅ Critique Result: PASS.")
                return None  # 返回 None 表示通过
            elif pass_status is False:
                logger.warning(f"   -> ⚠️ Critique Result: REVISE.")
                return critique_text # 返回具体的修改建议
            else:
                # 处理 'pass' 字段不是 true/false，或者不存在的情况
                error_msg = f"Invalid 'pass' value in LLM's JSON response (expected boolean, got {type(pass_status)}). Treating as failure."
                logger.error(f"   -> ❌ {error_msg}")
                return f"INVALID RESPONSE FORMAT: {error_msg} | Critique: {critique_text}"
            
        except Exception as e:
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
