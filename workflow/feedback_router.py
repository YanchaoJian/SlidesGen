import logging
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field

from agent.evaluator.prompts import FEEDBACK_ANALYSIS_SYSTEM_PROMPT, FEEDBACK_ANALYSIS_USER_TEMPLATE
from utils.llm_helpers import LLMConfig, create_llm

logger = logging.getLogger(__name__)


# --- Pydantic 模型 (保持不变) ---
class FeedbackAnalysis(BaseModel):
    """定义 LLM 的结构化输出模型"""
    scope: Literal["local", "global_style", "global_plan", "ambiguous"] = Field(
        description="The scope of the requested change."
    )
    target_pages: List[int] = Field(
        description="A list of page numbers to modify if the scope is 'local'.", 
        default=[]
    )

def analyze_feedback_with_llm(
    user_input: str,
    slide_count: int,
    llm_config: LLMConfig,
) -> FeedbackAnalysis:
    """使用 LLM 分析用户反馈的范围。"""
    try:
        llm = create_llm(llm_config, temperature=0)
        structured_llm = llm.with_structured_output(FeedbackAnalysis)

        # 使用从 prompts.py 导入的模板
        prompt = (
            FEEDBACK_ANALYSIS_SYSTEM_PROMPT + 
            "\n" + 
            FEEDBACK_ANALYSIS_USER_TEMPLATE.format(
                slide_count=slide_count,
                user_feedback=user_input
            )
        )
        
        result = structured_llm.invoke(prompt)
        logger.info(f"🔍 Feedback analyzed: Scope='{result.scope}', Target Pages={result.target_pages}")
        return result
    except Exception as e:
        logger.error(f"❌ Feedback analysis failed: {e}. Defaulting to 'ambiguous' scope.")
        # 返回一个安全的回退值
        return FeedbackAnalysis(scope="ambiguous", target_pages=[])
