"""
SVG 幻灯片生成器。

调用 LLM 根据 slide_plan + style_protocol 生成单页 SVG 源码。
对应原有 code_generator.py 的角色，但输出 SVG 而非 Python 代码。
"""

import logging
import re
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agents.composer.prompts import SVG_GENERATION_SYSTEM_PROMPT, build_svg_slide_prompt
from utils.llm import LLMConfig, create_llm

logger = logging.getLogger(__name__)


def extract_svg_content(text: str) -> Optional[str]:
    """
    从 LLM 响应文本中提取 SVG 源码。

    策略优先级：
    1. 匹配 ```xml 或 ```svg 代码块中的 <svg>...</svg>
    2. 匹配通用 ``` 代码块中的 <svg>...</svg>
    3. 直接匹配裸 <svg>...</svg> 标签
    """
    if not text:
        return None

    # 策略 1: 匹配 ```xml / ```svg 代码块
    pattern_tagged = r"```(?:xml|svg|html)\s*(.*?)```"
    blocks = re.findall(pattern_tagged, text, re.IGNORECASE | re.DOTALL)
    for block in blocks:
        svg = _find_svg_tag(block)
        if svg:
            return svg

    # 策略 2: 匹配通用 ``` 代码块
    pattern_generic = r"```(.*?)```"
    blocks = re.findall(pattern_generic, text, re.DOTALL)
    for block in blocks:
        svg = _find_svg_tag(block)
        if svg:
            return svg

    # 策略 3: 直接匹配裸 <svg>...</svg>
    svg = _find_svg_tag(text)
    if svg:
        return svg

    return None


def _find_svg_tag(text: str) -> Optional[str]:
    """从文本中提取 <svg ...>...</svg> 标签，支持多行。"""
    match = re.search(r"(<svg\b[^>]*>.*?</svg>)", text, re.DOTALL)
    return match.group(1).strip() if match else None


def generate_slide_svg(
    slide_plan: dict,
    style_protocol: str,
    llm_config: LLMConfig,
    total_pages: int = 10,
    slide_detail: Optional[str] = None,
    failed_svg: Optional[str] = None,
    error_context: Optional[str] = None,
    svg_verified: Optional[bool] = None,
) -> Optional[str]:
    """
    调用 LLM 生成单页幻灯片的 SVG 源码。

    Args:
        slide_plan: 单页计划 dict（含 slide_page, title, content 等）。
        style_protocol: 设计规范字符串。
        llm_config: LLM 配置。
        total_pages: 总页数（用于页码显示）。
        slide_detail: 由 expand_slide_plan 生成的详细页面描述（可选）。
        failed_svg: 上次失败的 SVG（重试时传入）。
        error_context: 上次的错误日志（重试时传入）。
        svg_verified: 上次 SVG 是否通过验证。

    Returns:
        提取出的 SVG 字符串，失败返回 None。
    """
    slide_page = slide_plan.get("slide_page", 1)
    is_retry = failed_svg and not svg_verified

    if is_retry:
        logger.info(f"   -> [Slide {slide_page}] SVG retry mode: fixing previous errors.")
    else:
        logger.info(f"   -> [Slide {slide_page}] SVG generation: creating from plan.")

    user_prompt = build_svg_slide_prompt(
        slide_plan=slide_plan,
        style_protocol=style_protocol,
        total_pages=total_pages,
        slide_detail=slide_detail,
        failed_svg=failed_svg if is_retry else "",
        error_context=error_context if is_retry else "",
    )

    try:
        llm = create_llm(llm_config, temperature=0.2)
        messages = [
            SystemMessage(content=SVG_GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)

        raw_content = response.content
        if isinstance(raw_content, list):
            # 某些 provider 返回 list[dict/text]，拼接为字符串
            parts = []
            for item in raw_content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
            raw_content = "".join(parts)

        svg = extract_svg_content(raw_content)
        if not svg:
            logger.error(f"   -> [Slide {slide_page}] Failed to extract SVG from LLM response.")
            logger.debug(f"   -> Raw response (first 500 chars): {str(raw_content)[:500]}")
        return svg

    except Exception as e:
        logger.error(f"   -> [Slide {slide_page}] LLM call failed: {e}")
        return None
