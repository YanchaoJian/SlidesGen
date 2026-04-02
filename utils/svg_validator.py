"""
SVG 验证与后处理模块。

验证 LLM 生成的 SVG 内容，执行后处理管线（圆角矩形转 path、展平 tspan、
嵌入图片等），并写入最终 SVG 文件。
"""

import logging
import os
import re
from pathlib import Path
from typing import Tuple
from xml.etree import ElementTree as ET

from utils.svg_finalize.svg_rect_to_path import process_svg
from utils.svg_finalize.flatten_tspan import flatten_text_with_tspans
from utils.svg_finalize.embed_images import embed_images_in_svg
from utils.svg_finalize.fix_image_aspect import fix_image_aspect_in_svg

logger = logging.getLogger(__name__)


# ==============================================================================
# SVG 验证
# ==============================================================================

# 禁用特性检测模式
_BANNED_PATTERNS = [
    (r"<clipPath[\s>]", "clipPath"),
    (r"<mask[\s>]", "mask"),
    (r"<style[\s>]", "<style> element"),
    (r'\bclass\s*=\s*"', "class attribute"),
    (r"<foreignObject[\s>]", "foreignObject"),
    (r"<symbol[\s>]", "symbol"),
    (r"<textPath[\s>]", "textPath"),
    (r"@font-face", "@font-face"),
    (r"<animate[\s>]", "animate"),
    (r"<set[\s>]", "<set> animation"),
    (r"<script[\s>]", "script"),
    (r"\bmarker-end\s*=", "marker-end"),
    (r"\bmarker-start\s*=", "marker-start"),
    (r"<iframe[\s>]", "iframe"),
    (r'fill\s*=\s*"rgba\(', "rgba() fill (use fill-opacity instead)"),
]


def validate_svg(svg_content: str) -> Tuple[bool, str]:
    """
    验证 SVG 内容的合法性。

    检查项：
    1. 基本 XML 结构（well-formed）
    2. 根元素为 <svg>
    3. 不包含禁用特性

    Returns:
        (is_valid, error_message)。有效时 error_message 为空字符串。
    """
    if not svg_content or not svg_content.strip():
        return False, "SVG content is empty."

    # 检查 XML well-formed
    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError as e:
        return False, f"SVG is not well-formed XML: {e}"

    # 检查根元素
    tag = root.tag
    # 去掉命名空间前缀
    if "}" in tag:
        tag = tag.split("}", 1)[1]
    if tag != "svg":
        return False, f"Root element is <{tag}>, expected <svg>."

    # 检查禁用特性
    violations = []
    for pattern, name in _BANNED_PATTERNS:
        if re.search(pattern, svg_content):
            violations.append(name)

    if violations:
        return False, f"SVG contains banned features: {', '.join(violations)}"

    return True, ""


# ==============================================================================
# SVG 后处理
# ==============================================================================

def finalize_single_svg(svg_path: str) -> Tuple[bool, str]:
    """
    对单个 SVG 文件执行后处理管线（原地修改文件）。

    处理步骤（按顺序）：
    1. 修复图片宽高比（防止 PPT 转换时拉伸）
    2. 嵌入外部图片为 base64
    3. 展平 tspan 为独立 text 元素
    4. 圆角矩形转为 path（防止转换时丢失圆角）

    Args:
        svg_path: SVG 文件路径。

    Returns:
        (success, error_message)
    """
    path = Path(svg_path)
    if not path.exists():
        return False, f"SVG file not found: {svg_path}"

    try:
        # Step 1: 修复图片宽高比
        try:
            fix_count = fix_image_aspect_in_svg(str(path), dry_run=False, verbose=False)
            if fix_count > 0:
                logger.debug(f"   -> Fixed aspect ratio for {fix_count} image(s)")
        except Exception as e:
            logger.warning(f"   -> fix_image_aspect skipped: {e}")

        # Step 2: 嵌入外部图片为 base64
        try:
            embed_count, _ = embed_images_in_svg(str(path), dry_run=False)
            if embed_count > 0:
                logger.debug(f"   -> Embedded {embed_count} image(s) as base64")
        except Exception as e:
            logger.warning(f"   -> embed_images skipped: {e}")

        # Step 3: 展平 tspan
        try:
            tree = ET.parse(str(path))
            changed = flatten_text_with_tspans(tree)
            if changed:
                tree.write(str(path), encoding="unicode", xml_declaration=False)
                logger.debug("   -> Flattened tspan elements")
        except Exception as e:
            logger.warning(f"   -> flatten_tspan skipped: {e}")

        # Step 4: 圆角矩形转 path
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            processed, count = process_svg(content, verbose=False)
            if count > 0:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(processed)
                logger.debug(f"   -> Converted {count} rounded rect(s) to path")
        except Exception as e:
            logger.warning(f"   -> svg_rect_to_path skipped: {e}")

        return True, ""

    except Exception as e:
        return False, f"SVG finalize failed: {e}"


# ==============================================================================
# SVG 执行（验证 + 后处理 + 写文件）
# ==============================================================================

def execute_svg(svg_content: str, output_svg_path: str) -> Tuple[bool, str]:
    """
    验证 SVG 内容，写入文件，并执行后处理。

    Args:
        svg_content: LLM 生成的原始 SVG 字符串。
        output_svg_path: SVG 文件保存路径。

    Returns:
        (success, error_message)。成功时 error_message 为空字符串。
    """
    # 1. 验证
    is_valid, error = validate_svg(svg_content)
    if not is_valid:
        logger.warning(f"   -> SVG validation failed: {error}")
        return False, error

    # 2. 写入文件
    os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    logger.info(f"   -> SVG saved: {output_svg_path}")

    # 3. 后处理
    success, finalize_error = finalize_single_svg(output_svg_path)
    if not success:
        return False, finalize_error

    logger.info(f"   -> SVG finalized: {output_svg_path}")
    return True, ""
