import json
import logging
import os
from typing import Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agent.composer.prompts import LAYOUT_DIRECTIVE_SYSTEM_PROMPT, LAYOUT_DIRECTIVE_USER_PROMPT
from utils.llm_helpers import LLMConfig, create_llm

logger = logging.getLogger(__name__)

def generate_layout_directive(
    slide_style_protocol: str,
    slide_content: Dict[str, Any],
    llm_config: LLMConfig,
    output_dir: str,
) -> Optional[str]:
    """
    为单张幻灯片生成自然语言布局指令 (Layout Directive)。

    Args:
        slide_style_protocol: 自然语言形式的主题风格描述。
        slide_content: 当前幻灯片的内容大纲字典。
        llm_config: LLM 连接配置。
        output_dir: 输出目录。

    Returns:
        包含布局指令的字符串，如果失败则返回 None。
    """
    slide_title = slide_content.get('title')
    slide_page = slide_content.get('slide_page')
    logger.info(f"🎨 Art Director is designing Slide {slide_page}: '{slide_title}'...")

    # 1. 初始化 LLM
    try:
        llm = create_llm(llm_config, temperature=0.3)
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM in layout engine: {e}")
        return None

    # 2. 填充 Prompt
    user_prompt_content = LAYOUT_DIRECTIVE_USER_PROMPT.format(
        style_description=slide_style_protocol,
        slide_content_json=json.dumps(slide_content, ensure_ascii=False, indent=2)
    )

    # 3. 构建消息并调用 LLM
    messages = [
        SystemMessage(content=LAYOUT_DIRECTIVE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt_content)
    ]
    
    try:
        logger.info("   -> Invoking LLM to generate layout directive...")
        response = llm.invoke(messages)
        directive = response.content.strip()
        
        # 简单的验证，确保返回不是空的
        if not directive:
            logger.warning("   -> ⚠️ LLM returned an empty layout directive.")
            return None

        # 保存directive为本地文本文件
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, "directive.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(directive)
        logger.info(f"   -> ✅ Layout directive for slide {slide_page} generated and saved to {filepath}")
        
        return directive
    except Exception as e:
        logger.error(f"❌ LLM call for layout directive failed: {e}")
        return None