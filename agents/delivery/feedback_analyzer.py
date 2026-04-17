"""
用户反馈分析器。

使用 LLM 结构化输出分析用户对最终 PPTX 的反馈意图，
决定后续路由（局部修改、全局风格重建、全局大纲重建、或结束）。
"""

import logging
from typing import List, Literal

from pydantic import BaseModel, Field, model_validator

from agents.delivery.prompts import FEEDBACK_ANALYSIS_SYSTEM_PROMPT, FEEDBACK_ANALYSIS_USER_TEMPLATE
from utils.llm import LLMConfig, create_llm, raise_if_fatal_llm_error, parse_json_response

logger = logging.getLogger(__name__)


class FeedbackAnalysis(BaseModel):
    """定义 LLM 的结构化输出模型"""
    scope: Literal["local", "global_style", "global_plan", "ambiguous"] = Field(
        description="The scope of the requested change."
    )
    target_pages: List[int] = Field(
        description="A list of page numbers to modify if the scope is 'local'.",
        default=[]
    )

    @model_validator(mode="after")
    def _sanitize(self) -> "FeedbackAnalysis":
        if self.scope != "local":
            self.target_pages = []
        if self.scope == "local" and not self.target_pages:
            logger.warning("   -> scope='local' but target_pages is empty. Downgrading to 'ambiguous'.")
            self.scope = "ambiguous"
            self.target_pages = []
        return self


def analyze_feedback(
    user_input: str,
    slide_count: int,
    llm_config: LLMConfig,
) -> FeedbackAnalysis:
    """使用 LLM 分析用户反馈的范围。"""
    try:
        llm = create_llm(llm_config, temperature=0)

        prompt = (
            FEEDBACK_ANALYSIS_SYSTEM_PROMPT +
            "\n" +
            FEEDBACK_ANALYSIS_USER_TEMPLATE.format(
                slide_count=slide_count,
                user_feedback=user_input,
            )
        )

        response = llm.invoke(prompt)
        result = parse_json_response(response.content)
        result = FeedbackAnalysis(**result)  # 验证并转换为 Pydantic 模型实例

        logger.info(f"   -> Feedback analyzed: Scope='{result.scope}', Target Pages={result.target_pages}")
        return result
    except Exception as e:
        raise_if_fatal_llm_error(e)
        logger.error(f"   -> Feedback analysis failed: {e}. Defaulting to 'ambiguous' scope.")
        return FeedbackAnalysis(scope="ambiguous", target_pages=[])
