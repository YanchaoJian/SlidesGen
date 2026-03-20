import logging
import re
from typing import List, Union, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agent.composer.prompts import (
    CODE_GENERATION_SYSTEM_PROMPT,
    CODE_GENERATION_USER_TEMPLATE,
)
from utils.llm_helpers import LLMConfig, create_llm

logger = logging.getLogger(__name__)

def extract_code_pieces(text: str) -> Optional[str]:
    """
    从 LLM 的文本响应中稳健地提取 Python 代码块。
    返回拼接后的单个代码字符串。
    """
    if not text:
        return None
    
    # 策略 1: 优先匹配明确标记为 Python 的代码块
    pattern_python = r"```(?:python|py)(.*?)```"
    code_pieces = re.findall(pattern_python, text, re.IGNORECASE | re.DOTALL)

    # 策略 2: 如果没找到，尝试匹配通用代码块
    if not code_pieces:
        pattern_generic = r"```(.*?)```"
        code_pieces = re.findall(pattern_generic, text, re.DOTALL)
        
    # 策略 3: 兜底，如果文本看起来像代码
    if not code_pieces:
        keywords = ["import pptx", "def ", "from pptx.util import"]
        if any(k in text for k in keywords):
            return text.strip()

    if not code_pieces:
        return None

    # 清理并拼接所有找到的代码块
    cleaned_pieces = [code.strip() for code in code_pieces if code.strip()]
    return '\n\n'.join(cleaned_pieces)


def generate_slide_code(
    output_pptx_path: str,
    llm_config: LLMConfig,
    code_directive: Optional[str] = None,
    failed_code: Optional[str] = None,
    error_context: Optional[str] = None,
    slide_code_verified: Optional[bool] = None,
) -> Optional[str]:
    """
    一个多模态的代码生成/修复函数。
    - 如果提供了 directive_text，则进入“首次生成”模式。
    - 如果提供了 failed_code 和 error_context，则进入“代码修复”模式。
    """
    logger.info("   🤖 Coder Agent is generating Python script...")
    
    system_prompt = CODE_GENERATION_SYSTEM_PROMPT
    # --- 根据输入参数，动态选择“模式”和构建 Prompt ---
    is_fixing_mode = failed_code and not slide_code_verified

    if is_fixing_mode:
        # 模式: 代码修复 (Code Fixing)
        logger.info("   -> Mode: Fixing existing code based on error log.")
        user_prompt_content = CODE_GENERATION_USER_TEMPLATE.format(
            code_directive=code_directive,
            output_pptx_path=output_pptx_path,
            failed_code=failed_code,
            error_context=error_context
        )
    else:
        # 模式: 首次生成 (Initial Generation)
        logger.info("   -> Mode: Generating new code from layout directive.")
        user_prompt_content = CODE_GENERATION_USER_TEMPLATE.format(
            code_directive=code_directive,
            output_pptx_path=output_pptx_path,
            failed_code="",
            error_context=""
        )

    # --- 调用 LLM (通用逻辑) ---
    try:
        llm = create_llm(llm_config, temperature=0.0)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt_content),
        ]
        response = llm.invoke(messages)
        
        code = extract_code_pieces(response.content)
        return code

    except Exception as e:
        logger.error(f"   ❌ Coder Agent LLM call failed: {e}")
        return None