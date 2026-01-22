# filepath: src/composer/layout_engine.py
import json
import logging
import os
from typing import Dict, Any, Optional

# 使用 LangChain 统一 LLM 调用
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# 假设 prompts 位于 src/composer/prompts.py
# 注意：根据你的项目结构，可能需要调整路径
from agent.composer.prompts import LAYOUT_DIRECTIVE_SYSTEM_PROMPT, LAYOUT_DIRECTIVE_USER_PROMPT

logger = logging.getLogger(__name__)

def generate_layout_directive(
    slide_style_protocol: Dict[str, Any],
    slide_content: Dict[str, Any],
    api_key: str,
    base_url: str,
    model_name: str,
    output_dir: str,
) -> Optional[str]:
    """
    为单张幻灯片生成自然语言布局指令 (Layout Directive)。

    Args:
        style_protocol: 包含视觉风格规则的字典。
        slide_content: 当前幻灯片的内容大纲字典。
        api_key: OpenAI API key。
        base_url: OpenAI API base URL。
        model_name: 使用的 LLM 模型名称。
        user_feedback: (可选) 用户针对此页的特定修改反馈。

    Returns:
        包含布局指令的字符串，如果失败则返回 None。
    """
    slide_title = slide_content.get('title')
    slide_page = slide_content.get('slide_page')
    logger.info(f"🎨 Art Director is designing Slide {slide_page}: '{slide_title}'...")

    # 1. 初始化 LLM
    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.3, # 保持一定的设计灵活性
            api_key=api_key,
            base_url=base_url
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM in layout engine: {e}")
        return None
    
    # 2. 填充 Prompt
    # 使用 json.dumps 将字典数据格式化为字符串嵌入到 Prompt 中
    user_prompt_content = LAYOUT_DIRECTIVE_USER_PROMPT.format(
        protocol_json=json.dumps(slide_style_protocol, ensure_ascii=False, indent=2),
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