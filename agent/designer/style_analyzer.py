import os
import json
import logging
from typing import Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agent.designer.prompts import ANALYZE_STYLE_SYSTEM_PROMPT, ANALYZE_STYLE_USER_PROMPT, ANALYZE_STYLE_REFINEMENT_USER_PROMPT
from utils.llm_helpers import LLMConfig, create_llm, encode_image_to_base64, extract_json_from_response

logger = logging.getLogger(__name__)

def analyze_style(
    style_image_path: str,
    output_dir: str,
    llm_config: LLMConfig,
    previous_protocol: Optional[Dict[str, Any]] = None,
    previous_protocol_critique: Optional[str] = None,
    style_protocol_retry_count: Optional[int] = 0,
    style_protocol_verified: Optional[bool] = False
) -> Optional[Dict[str, Any]]:
    """
    调用 Vision LLM 分析 PPT 截图风格，并返回结构化的字典。

    Args:
        style_image_path: 参考图的文件路径。
        output_dir: 输出目录。
        llm_config: LLM 连接配置。

    Returns:
        一个包含视觉协议的字典，如果失败则返回 None。
    """
    logger.info(f"🎨 Analyzing style from image: {os.path.basename(style_image_path)}")

    try:
        base64_image = encode_image_to_base64(style_image_path)
    except Exception:
        return None

    # 1. 初始化 LLM
    llm = create_llm(llm_config, temperature=0.1)

    if previous_protocol and not style_protocol_verified:
        # 将 JSON 对象转为格式化的字符串，方便 LLM 阅读
        prev_json_str = json.dumps(previous_protocol, ensure_ascii=False, indent=2)
        
        # 填充模板
        user_prompt = ANALYZE_STYLE_REFINEMENT_USER_PROMPT.format(
            previous_protocol_json=prev_json_str,
            critique_text=previous_protocol_critique
        )
        
        logging.info("Using previous style protocol and critique for refinement.")
    else:
        user_prompt = ANALYZE_STYLE_USER_PROMPT
    
    # 2. 构建消息体 
    messages = [
        SystemMessage(content=ANALYZE_STYLE_SYSTEM_PROMPT),
        HumanMessage(content=[
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ])
    ]

    # 3. 调用 LLM 并解析结果
    try:
        response = llm.invoke(messages)
        content = response.content
        
        # 3.1 提取并解析 JSON
        style_data = extract_json_from_response(content)
        if not style_data:
            logger.error("❌ Failed to parse JSON from LLM response.")
            return None

        logger.info("✅ Style analysis successful.")

        # 将结果保存到文件
        result_dir = os.path.join(output_dir, "style")
        os.makedirs(result_dir, exist_ok=True)
        version = style_protocol_retry_count  # None/0 视为首次
        protocol_path = os.path.join(result_dir, f"style_protocol_v{version}.json")
        with open(protocol_path, "w", encoding='utf-8') as f:
            json.dump(style_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Style protocol saved to {protocol_path}")
        return style_data

    except Exception as e:
        logger.error(f"❌ LLM call for style analysis failed: {e}")
        return None