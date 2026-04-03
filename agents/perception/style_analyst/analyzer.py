import os
import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agents.perception.style_analyst.prompts import ANALYZE_STYLE_SYSTEM_PROMPT, ANALYZE_STYLE_USER_PROMPT, ANALYZE_STYLE_REFINEMENT_USER_PROMPT
from utils.llm import LLMConfig, create_llm, encode_image_to_base64

logger = logging.getLogger(__name__)

def analyze_style(
    style_image_path: str,
    output_dir: str,
    llm_config: LLMConfig,
    previous_protocol: Optional[str] = None,
    previous_protocol_critique: Optional[str] = None,
    style_protocol_retry_count: Optional[int] = 0,
    style_protocol_verified: Optional[bool] = False
) -> Optional[str]:
    """
    调用 Vision LLM 分析 PPT 截图风格，返回自然语言形式的主题风格描述。

    Args:
        style_image_path: 参考图的文件路径。
        output_dir: 输出目录。
        llm_config: LLM 连接配置。
        previous_protocol: 上一轮的风格描述文本（用于迭代优化）。
        previous_protocol_critique: 上一轮的审查反馈。
        style_protocol_retry_count: 重试次数。
        style_protocol_verified: 是否已通过验证。

    Returns:
        自然语言形式的主题风格描述字符串，如果失败则返回 None。
    """
    logger.info(f"🎨 Analyzing style from image: {os.path.basename(style_image_path)}")

    try:
        base64_image = encode_image_to_base64(style_image_path)
    except Exception:
        return None

    # 1. 初始化 LLM
    llm = create_llm(llm_config, temperature=0.1)

    if previous_protocol and not style_protocol_verified:
        # 填充优化模板
        user_prompt = ANALYZE_STYLE_REFINEMENT_USER_PROMPT.format(
            previous_protocol_text=previous_protocol,
            critique_text=previous_protocol_critique
        )

        logging.info("Using previous style description and critique for refinement.")
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

    # 3. 调用 LLM 并获取结果
    try:
        response = llm.invoke(messages)
        style_description = response.content.strip()

        if not style_description:
            logger.error("❌ LLM returned empty style description.")
            return None

        logger.info("✅ Style analysis successful.")

        # 将结果保存到文件
        result_dir = os.path.join(output_dir, "style")
        os.makedirs(result_dir, exist_ok=True)
        version = style_protocol_retry_count  # None/0 视为首次
        protocol_path = os.path.join(result_dir, f"style_protocol_v{version}.md")
        with open(protocol_path, "w", encoding='utf-8') as f:
            f.write(style_description)
        logger.info(f"Style description saved to {protocol_path}")
        return style_description

    except Exception as e:
        logger.error(f"❌ LLM call for style analysis failed: {e}")
        return None
