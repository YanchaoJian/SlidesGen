"""
CRAP 设计原则优化器。

调用 LLM 根据 CRAP 设计原则对 SVG 源码进行代码级视觉优化。
"""

import logging
import re
from typing import Optional
from xml.etree import ElementTree as ET

from langchain_core.messages import SystemMessage, HumanMessage

from agents.svg_optimizer.prompts import CRAP_OPTIMIZER_SYSTEM_PROMPT, CRAP_OPTIMIZER_USER_PROMPT
from agents.slide_composer.svg_generator import extract_svg_content
from utils.svg_validator import _check_geometry
from utils.llm import LLMConfig, create_llm

logger = logging.getLogger(__name__)


def _get_canvas_dimensions(svg_code: str) -> tuple:
    """从 SVG 代码中提取画布尺寸。"""
    # 尝试 viewBox
    match = re.search(r'viewBox\s*=\s*"([^"]+)"', svg_code)
    if match:
        parts = match.group(1).split()
        if len(parts) == 4:
            try:
                return int(float(parts[2])), int(float(parts[3]))
            except ValueError:
                pass
    # 回退到 width/height
    w_match = re.search(r'\bwidth\s*=\s*"(\d+)"', svg_code)
    h_match = re.search(r'\bheight\s*=\s*"(\d+)"', svg_code)
    w = int(w_match.group(1)) if w_match else 1280
    h = int(h_match.group(1)) if h_match else 720
    return w, h


def optimize_svg_crap(
    svg_code: str,
    llm_config: LLMConfig,
) -> Optional[str]:
    """
    使用 CRAP 设计原则优化 SVG 代码。

    Args:
        svg_code: 原始 SVG 源码。
        llm_config: LLM 配置。

    Returns:
        优化后的 SVG 字符串，失败返回 None。
    """
    if not svg_code:
        return None

    canvas_w, canvas_h = _get_canvas_dimensions(svg_code)
    logger.info(f"   -> CRAP optimizer: canvas {canvas_w}x{canvas_h}, input {len(svg_code)} chars")

    # 运行几何预检，将问题作为提示信息传给 LLM
    geometry_warnings = ""
    try:
        root = ET.fromstring(svg_code)
        geo_issues = _check_geometry(root)
        if geo_issues:
            geometry_warnings = "\n".join(f"- {w}" for w in geo_issues)
            logger.info(f"   -> CRAP optimizer: {len(geo_issues)} geometry issue(s) detected, passing to LLM for fixing.")
    except ET.ParseError:
        pass  # SVG 已通过 validate_svg，这里不应该失败

    geo_section = ""
    if geometry_warnings:
        geo_section = (
            "\n## Pre-detected Geometry Issues (MUST FIX FIRST)\n\n"
            "The following geometry problems were detected by automated analysis. "
            "You MUST fix all of them:\n\n"
            f"{geometry_warnings}\n"
        )

    user_prompt = CRAP_OPTIMIZER_USER_PROMPT.format(
        canvas_width=canvas_w,
        canvas_height=canvas_h,
        geo_section=geo_section,
        svg_code=svg_code,
    )

    try:
        llm = create_llm(llm_config, temperature=0.1)
        messages = [
            SystemMessage(content=CRAP_OPTIMIZER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)

        raw_content = response.content
        if isinstance(raw_content, list):
            parts = []
            for item in raw_content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif isinstance(item, str):
                    parts.append(item)
            raw_content = "".join(parts)

        optimized_svg = extract_svg_content(raw_content)
        if not optimized_svg:
            logger.warning("   -> CRAP optimizer: failed to extract SVG from LLM response. Using original.")
            return None

        logger.info(f"   -> CRAP optimizer: output {len(optimized_svg)} chars")
        return optimized_svg

    except Exception as e:
        logger.error(f"   -> CRAP optimizer LLM call failed: {e}")
        return None
