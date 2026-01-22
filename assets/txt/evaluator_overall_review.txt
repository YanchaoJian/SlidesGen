import logging
from typing import Dict, Any, Optional, List, Literal
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 从 prompts.py 导入新的模板
from agent.evaluator.prompts import FEEDBACK_ANALYSIS_SYSTEM_PROMPT, FEEDBACK_ANALYSIS_USER_TEMPLATE
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

# --- 辅助函数：封装 LLM 分析逻辑 ---
def _analyze_feedback_with_llm(
    user_input: str,
    slide_count: int,
    llm_config: dict
) -> FeedbackAnalysis:
    """使用 LLM 分析用户反馈的范围。"""
    try:
        llm = ChatOpenAI(
            model=llm_config["model_name"], 
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"], 
            temperature=0
        )
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
