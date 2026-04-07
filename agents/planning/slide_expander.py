"""
单页大纲扩展器。

接收简要的 slide plan + design specification，
调用 LLM 生成详细的页面描述，供下游 SVG 生成节点使用。
"""

import json
import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agents.planning.prompts import (
    EXPAND_SLIDE_PLAN_SYSTEM_PROMPT,
    EXPAND_SLIDE_PLAN_USER_PROMPT,
)
from utils.llm import LLMConfig, create_llm, raise_if_fatal_llm_error

logger = logging.getLogger(__name__)


def expand_slide_plan(
    slide_plan: dict,
    style_protocol: str,
    llm_config: LLMConfig,
) -> Optional[str]:
    """
    将简要的单页大纲扩展为详细的页面描述。

    Args:
        slide_plan: 单页计划 dict（含 slide_page, title, content 等）。
        style_protocol: 设计规范字符串。
        llm_config: LLM 配置。

    Returns:
        详细的页面描述字符串，失败返回 None。
    """
    slide_page = slide_plan.get("slide_page", "?")
    logger.info(f"   -> [Slide {slide_page}] Expanding slide plan...")

    user_prompt = EXPAND_SLIDE_PLAN_USER_PROMPT.format(
        slide_plan_json=json.dumps(slide_plan, ensure_ascii=False, indent=2),
        style_protocol=style_protocol,
    )

    try:
        llm = create_llm(llm_config, temperature=0.15)
        messages = [
            SystemMessage(content=EXPAND_SLIDE_PLAN_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        detail = response.content.strip()

        if not detail:
            logger.warning(f"   -> [Slide {slide_page}] LLM returned empty expansion.")
            return None

        logger.info(f"   -> [Slide {slide_page}] Slide plan expanded ({len(detail)} chars).")
        return detail

    except Exception as e:
        raise_if_fatal_llm_error(e)
        logger.error(f"   -> [Slide {slide_page}] Slide plan expansion failed: {e}")
        return None
