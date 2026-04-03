"""
SVG 验证与后处理模块。

验证 LLM 生成的 SVG 内容，执行后处理管线（圆角矩形转 path、展平 tspan、
嵌入图片等），并写入最终 SVG 文件。
"""

import logging
import re
from pathlib import Path
from typing import Tuple
from xml.etree import ElementTree as ET

from utils.svg_finalize.svg_rect_to_path import process_svg
from utils.svg_finalize.flatten_tspan import flatten_text_with_tspans
from utils.svg_finalize.embed_images import embed_images_in_svg
from utils.svg_finalize.fix_image_aspect import fix_image_aspect_in_svg
from utils.svg_finalize.add_image_card import add_image_cards

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


def _get_canvas_size(root: ET.Element) -> tuple:
    """从 SVG 根元素获取画布尺寸。"""
    viewbox = root.get("viewBox")
    if viewbox:
        parts = viewbox.split()
        if len(parts) == 4:
            try:
                return float(parts[2]), float(parts[3])
            except ValueError:
                pass
    # 回退到 width/height 属性
    try:
        w = float(root.get("width", "1280"))
        h = float(root.get("height", "720"))
        return w, h
    except ValueError:
        return 1280.0, 720.0


def _parse_float(value, default=0.0) -> float:
    """安全解析浮点数属性。"""
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_bounding_box(elem: ET.Element, ns: str) -> tuple:
    """
    获取元素的近似 bounding box (x, y, w, h)。
    仅处理 rect, image, text 等常见元素。
    返回 None 表示无法计算。
    """
    tag = elem.tag
    if "}" in tag:
        tag = tag.split("}", 1)[1]

    if tag in ("rect", "image"):
        x = _parse_float(elem.get("x"))
        y = _parse_float(elem.get("y"))
        w = _parse_float(elem.get("width"))
        h = _parse_float(elem.get("height"))
        if w > 0 and h > 0:
            return (x, y, w, h)

    elif tag == "text":
        x = _parse_float(elem.get("x"))
        y = _parse_float(elem.get("y"))
        font_size = _parse_float(elem.get("font-size"), 18.0)
        # 估算文本块高度：计算 tspan 数量
        tspan_count = len(list(elem.iter(f"{ns}tspan" if ns else "tspan")))
        if tspan_count <= 1:
            # 检查无命名空间的 tspan
            tspan_count = max(1, len([c for c in elem if "tspan" in (c.tag.split("}")[-1] if "}" in c.tag else c.tag)]))
        tspan_count = max(1, tspan_count)
        est_height = tspan_count * font_size * 1.6
        # 文本 y 通常是 baseline，向上偏移一个行高作为 top
        top_y = y - font_size
        # 估算文本宽度：基于最长的文本内容或合理默认值
        text_content = elem.text or ""
        for child in elem:
            child_text = child.text or ""
            if len(child_text) > len(text_content):
                text_content = child_text
        est_width = max(len(text_content) * font_size * 0.55, font_size * 5)
        # 上限不超过画布剩余宽度
        est_width = min(est_width, 1280 - x) if x >= 0 else est_width
        return (x, top_y, est_width, est_height)

    return None


def _boxes_overlap(a: tuple, b: tuple, min_gap: int = 0) -> bool:
    """检查两个 bounding box 是否重叠（含最小间距检查）。"""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    # 水平方向无交集
    if ax + aw + min_gap <= bx or bx + bw + min_gap <= ax:
        return False
    # 垂直方向无交集
    if ay + ah + min_gap <= by or by + bh + min_gap <= ay:
        return False
    return True


def check_geometry(root: ET.Element) -> list:
    """
    检查 SVG 元素的几何合理性。

    返回警告消息列表（空列表表示无问题）。
    仅检测严重的越界和重叠问题。
    """
    warnings = []
    canvas_w, canvas_h = _get_canvas_size(root)

    ns = ""
    tag = root.tag
    if "}" in tag:
        ns = tag.split("}")[0] + "}"

    # 收集所有内容元素的 bounding box（跳过第一个 rect 即背景）
    content_boxes = []  # (element_desc, bbox)
    skip_first_rect = True

    for elem in root.iter():
        etag = elem.tag
        if "}" in etag:
            etag = etag.split("}", 1)[1]

        # 跳过 defs 内的元素
        parent = None
        for p in root.iter():
            ptag = p.tag.split("}")[-1] if "}" in p.tag else p.tag
            if ptag == "defs":
                for child in p.iter():
                    if child is elem:
                        parent = "defs"
                        break
            if parent:
                break
        if parent == "defs":
            continue

        if etag not in ("rect", "image", "text"):
            continue

        # 跳过背景 rect（第一个全画布 rect）
        if skip_first_rect and etag == "rect":
            w = _parse_float(elem.get("width"))
            h = _parse_float(elem.get("height"))
            if w >= canvas_w * 0.9 and h >= canvas_h * 0.9:
                skip_first_rect = False
                continue

        bbox = _get_bounding_box(elem, ns)
        if bbox is None:
            continue

        x, y, w, h = bbox

        # 1. 越界检查（允许少量溢出 5px）
        tolerance = 5
        if x + w > canvas_w + tolerance:
            desc = f"<{etag}> at x={x}, width={w}"
            warnings.append(f"Out of bounds (right): {desc} exceeds canvas width {canvas_w}. "
                            f"Fix: reduce width or move left so that x + width ≤ {canvas_w}.")
        if y + h > canvas_h + tolerance:
            desc = f"<{etag}> at y={y}, height={h}"
            warnings.append(f"Out of bounds (bottom): {desc} exceeds canvas height {canvas_h}. "
                            f"Fix: reduce height or move up so that y + height ≤ {canvas_h}.")

        # 收集用于重叠检测
        elem_desc = f"<{etag} x='{x}' y='{y}' w='{w}' h='{h}'>"
        content_boxes.append((elem_desc, bbox))

    # 2. 重叠检测（仅检查 text-image 和 text-text 重叠，跳过装饰性 rect）
    for i in range(len(content_boxes)):
        for j in range(i + 1, len(content_boxes)):
            desc_a, box_a = content_boxes[i]
            desc_b, box_b = content_boxes[j]

            # 只检查涉及 text 或 image 的重叠
            is_content_a = "text" in desc_a or "image" in desc_a
            is_content_b = "text" in desc_b or "image" in desc_b
            if not (is_content_a and is_content_b):
                continue

            if _boxes_overlap(box_a, box_b):
                warnings.append(f"Overlap detected: {desc_a} collides with {desc_b}. "
                                f"Fix: adjust x/y/width/height to ensure ≥20px gap between elements.")

    # 限制警告数量，避免噪音过多
    if len(warnings) > 5:
        warnings = warnings[:5]
        warnings.append(f"... and more geometry issues. Fix the above first.")

    return warnings


# ==============================================================================
# SVG 后处理
# ==============================================================================

def finalize_single_svg(svg_path: str) -> Tuple[bool, str]:
    """
    对单个 SVG 文件执行后处理管线（原地修改文件）。

    处理步骤（按顺序）：
    1. 修复图片宽高比（防止 PPT 转换时拉伸）
    2. 为图片添加白色底卡（消除论文白底图与彩色幻灯片背景的割裂感）
    3. 嵌入外部图片为 base64
    4. 展平 tspan 为独立 text 元素
    5. 圆角矩形转为 path（防止转换时丢失圆角）

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

        # Step 2: 为图片添加白色底卡
        try:
            tree = ET.parse(str(path))
            card_count = add_image_cards(tree)
            if card_count > 0:
                tree.write(str(path), encoding="unicode", xml_declaration=False)
                logger.debug(f"   -> Added white card backing for {card_count} image(s)")
        except Exception as e:
            logger.warning(f"   -> add_image_card skipped: {e}")

        # Step 3: 嵌入外部图片为 base64
        try:
            embed_count, _ = embed_images_in_svg(str(path), dry_run=False)
            if embed_count > 0:
                logger.debug(f"   -> Embedded {embed_count} image(s) as base64")
        except Exception as e:
            logger.warning(f"   -> embed_images skipped: {e}")

        # Step 4: 展平 tspan
        try:
            tree = ET.parse(str(path))
            changed = flatten_text_with_tspans(tree)
            if changed:
                tree.write(str(path), encoding="unicode", xml_declaration=False)
                logger.debug("   -> Flattened tspan elements")
        except Exception as e:
            logger.warning(f"   -> flatten_tspan skipped: {e}")

        # Step 5: 圆角矩形转 path
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
