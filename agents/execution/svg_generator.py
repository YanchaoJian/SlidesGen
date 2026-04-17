"""
SVG 幻灯片生成器。

调用 LLM 根据 slide_plan + style_protocol 生成单页 SVG 源码。
对应原有 code_generator.py 的角色，但输出 SVG 而非 Python 代码。
"""

import logging
import re
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from agents.execution.prompts import SVG_GENERATION_SYSTEM_PROMPT
from utils.llm import LLMConfig, create_llm, raise_if_fatal_llm_error

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


def build_svg_slide_prompt(
    slide_plan: dict,
    style_protocol: str,
    total_pages: int = 10,
    slide_detail: str = "",
    failed_svg: str = "",
    error_context: str = "",
    design_critique: str = "",
) -> str:
    """
    构建单页 SVG 生成的 user prompt。

    Args:
        slide_plan: 单页幻灯片计划 dict，包含 slide_page, title, content,
                    includes_figure, figure_reference, includes_table,
                    table_reference, includes_equation, equation_reference,
                    presenter_notes 等字段。
        style_protocol: 设计规范字符串（来自 style_analyst）。
        total_pages: 总页数，用于页码显示。
        slide_detail: 由 expand_slide_plan 生成的详细页面描述（可选）。
        failed_svg: 上次失败的 SVG 代码（重试时传入）。
        error_context: 上次的错误日志（语法/结构验证失败时传入）。
        design_critique: 视觉评审反馈（设计质量检查未通过时传入）。

    Returns:
        完整的 user prompt 字符串。
    """
    page = slide_plan.get("slide_page", 1)
    title = slide_plan.get("title", "")
    content_items = slide_plan.get("content", [])

    # ── 构建内容描述 ──
    sections = []

    sections.append(f"## Slide {page} / {total_pages}\n")

    if not slide_detail:
        # 设计规范（从参考图提取的主题风格）
        sections.append("### Design Specification\n")
        sections.append("Follow the color scheme, typography, layout principles, and visual features ")
        sections.append("defined below. These override the default values in the system prompt.\n")
        sections.append(f"{style_protocol}\n")

        # 页面内容
        sections.append("### Page Content\n")
        sections.append(f"**Title**: {title}\n")

        if content_items:
            sections.append("**Body Points**:")
            for i, item in enumerate(content_items, 1):
                sections.append(f"  {i}. {item}")
            sections.append("")

    # 详细页面描述（由 expand_slide_plan 生成）
    sections.append("### Detailed Slide Description\n")
    sections.append("The following is a detailed layout and content description expanded from the outline. ")
    sections.append("Use this as the primary guide for element placement and visual decisions.\n")
    sections.append(f"{slide_detail}\n")

    # 图片引用
    if slide_plan.get("includes_figure") and slide_plan.get("figure_reference"):
        fig = slide_plan["figure_reference"]
        fig_path = fig.get("path", "")
        fig_caption = fig.get("caption", "")
        fig_dims = fig.get("dimensions") or {}
        sections.append("**Figure**:")
        sections.append(f"  - Path: `{fig_path}`")
        sections.append(f"  - Caption: {fig_caption}")
        if fig_dims:
            w = fig_dims.get("width")
            h = fig_dims.get("height")
            ar = fig_dims.get("aspect_ratio")
            orient = fig_dims.get("orientation", "")
            sections.append(
                f"  - Intrinsic size: {w}x{h}px ({orient}, aspect ratio W/H={ar}). "
                f"Allocate the image card with this aspect ratio to avoid distortion or cropping."
            )
            preserve = "xMidYMid meet"
        else:
            preserve = "xMidYMid slice"
        sections.append(f'  - Use: `<image href="{fig_path}" preserveAspectRatio="{preserve}"/>`')
        sections.append("")

    # 表格引用
    if slide_plan.get("includes_table") and slide_plan.get("table_reference"):
        tbl = slide_plan["table_reference"]
        sections.append("**Table** (render as SVG rectangles + text, NOT as HTML):")
        sections.append(f"  - Caption: {tbl.get('caption', '')}")
        sections.append(f"  - Data:\n```\n{tbl.get('markdown', '')}\n```")
        sections.append("")

    # 公式引用
    if slide_plan.get("includes_equation") and slide_plan.get("equation_reference"):
        eq = slide_plan["equation_reference"]
        sections.append("**Equation** (render as SVG `<text>` with mathematical symbols):")
        sections.append(f"  - LaTeX: `{eq.get('latex', '')}`")
        sections.append(f"  - Context: {eq.get('context', '')}")
        sections.append("")
        
    # 页面类型提示
    if page == 1:
        sections.append("### Layout Hint\n")
        sections.append("This is the **cover page**. Use a visually striking layout: "
                        "large centered title, subtitle below, decorative elements, "
                        "and the page background should make a strong first impression.\n")
    elif page == total_pages:
        sections.append("### Layout Hint\n")
        sections.append("This is the **closing page**. Use a clean, memorable layout: "
                        "thank-you message, key takeaway, or call to action.\n")

    # 重试上下文
    if failed_svg or error_context or design_critique:
        sections.append("### ⚠️ Retry Context\n")

        if design_critique:
            sections.append("The previous SVG **passed syntax validation** but **failed visual design review**. "
                            "A visual auditor examined the rendered slide screenshot and found layout/aesthetic issues.\n")
            sections.append(f"**Visual Critique (you MUST fix all issues listed below)**:\n```\n{design_critique}\n```\n")
            sections.append("**Instructions**: Carefully read the critique above. Each issue includes the specific SVG element "
                            "and attribute that needs to change, along with the suggested fix values. Apply ALL suggested fixes "
                            "to the previous SVG below. Do NOT just regenerate from scratch — modify the specific coordinates, "
                            "sizes, and positions mentioned in the critique.\n")
        elif error_context:
            sections.append("The previous SVG generation failed **syntax/structure validation**. Fix the issues below.\n")
            sections.append(f"**Error Log**:\n```\n{error_context}\n```\n")

        if failed_svg:
            sections.append(f"**Previous SVG (apply fixes to this)**:\n```xml\n{failed_svg}\n```\n")

    # 最终指令
    sections.append("---\n")
    sections.append("Generate the complete SVG source code for this slide. "
                    "Output only the SVG, nothing else.")

    return "\n".join(sections)


def generate_slide_svg(
    slide_plan: dict,
    style_protocol: str,
    llm_config: LLMConfig,
    total_pages: int = 10,
    slide_detail: Optional[str] = None,
    failed_svg: Optional[str] = None,
    error_context: Optional[str] = None,
    svg_verified: Optional[bool] = None,
    design_critique: Optional[str] = None,
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
        design_critique: 视觉评审反馈（设计质量检查未通过时传入）。

    Returns:
        提取出的 SVG 字符串，失败返回 None。
    """
    slide_page = slide_plan.get("slide_page", 1)
    is_retry = failed_svg and not svg_verified
    is_design_retry = bool(failed_svg and design_critique)

    if is_design_retry:
        logger.info(f"   -> [Slide {slide_page}] SVG design retry mode: fixing visual issues from critique.")
    elif is_retry:
        logger.info(f"   -> [Slide {slide_page}] SVG retry mode: fixing previous errors.")
    else:
        logger.info(f"   -> [Slide {slide_page}] SVG generation: creating from plan.")

    user_prompt = build_svg_slide_prompt(
        slide_plan=slide_plan,
        style_protocol=style_protocol,
        total_pages=total_pages,
        slide_detail=slide_detail,
        failed_svg=failed_svg if (is_retry or is_design_retry) else "",
        error_context=error_context if is_retry else "",
        design_critique=design_critique if is_design_retry else "",
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
        raise_if_fatal_llm_error(e)
        logger.error(f"   -> [Slide {slide_page}] LLM call failed: {e}")
        return None
