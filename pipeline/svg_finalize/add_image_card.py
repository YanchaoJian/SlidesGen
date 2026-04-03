"""
SVG Image Card Backing Tool

为 SVG 中的 <image> 元素自动添加白色圆角矩形底卡。
学术论文提取的图片通常带有白色背景，当 PPT 背景带有颜色时会产生割裂感。
白色底卡 + 阴影让白背景看起来像刻意的"卡片"效果。

作为 SVG finalize 管线的保底步骤：如果 LLM 生成时已经加了底卡，则跳过。
"""

import logging
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

# 底卡参数
CARD_PADDING = 12
CARD_RX = 8
CARD_FILL = "#FFFFFF"

# 标准阴影 filter（与 prompts.py 中的模板一致）
SHADOW_FILTER_ID = "imgCardShadow"
SHADOW_FILTER_XML = (
    f'<filter id="{SHADOW_FILTER_ID}" x="-15%" y="-15%" width="140%" height="140%">'
    '<feGaussianBlur in="SourceAlpha" stdDeviation="6"/>'
    '<feOffset dx="0" dy="4" result="offsetBlur"/>'
    '<feFlood flood-color="#000000" flood-opacity="0.12" result="shadowColor"/>'
    '<feComposite in="shadowColor" in2="offsetBlur" operator="in" result="shadow"/>'
    '<feMerge>'
    '<feMergeNode in="shadow"/>'
    '<feMergeNode in="SourceGraphic"/>'
    '</feMerge>'
    '</filter>'
)


def _parse_float(value, default=0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _has_card_backing(image_elem: ET.Element, parent: ET.Element, ns: str) -> bool:
    """
    检查 <image> 前面是否已有白色 rect 底卡。

    判定条件：紧邻 image 之前的兄弟元素是 <rect>，且：
    - fill 为 #FFFFFF 或 #fff 或 white
    - 尺寸略大于 image（差值在 0~50px 内）
    """
    children = list(parent)
    idx = None
    for i, child in enumerate(children):
        if child is image_elem:
            idx = i
            break

    if idx is None or idx == 0:
        return False

    prev = children[idx - 1]
    prev_tag = prev.tag.split("}")[-1] if "}" in prev.tag else prev.tag
    if prev_tag != "rect":
        return False

    fill = (prev.get("fill") or "").strip().lower()
    if fill not in ("#ffffff", "#fff", "white"):
        return False

    # 检查尺寸是否"包裹"了 image
    img_x = _parse_float(image_elem.get("x"))
    img_y = _parse_float(image_elem.get("y"))
    img_w = _parse_float(image_elem.get("width"))
    img_h = _parse_float(image_elem.get("height"))

    rect_x = _parse_float(prev.get("x"))
    rect_y = _parse_float(prev.get("y"))
    rect_w = _parse_float(prev.get("width"))
    rect_h = _parse_float(prev.get("height"))

    # 底卡应略大于图片：rect 起点 ≤ image 起点，rect 终点 ≥ image 终点
    if (rect_x <= img_x + 2 and rect_y <= img_y + 2
            and rect_x + rect_w >= img_x + img_w - 2
            and rect_y + rect_h >= img_y + img_h - 2):
        return True

    return False


def _is_fullscreen_image(image_elem: ET.Element, canvas_w: float, canvas_h: float) -> bool:
    """判断是否为全屏背景图片（覆盖 ≥90% 画布），这类图片不需要底卡。"""
    w = _parse_float(image_elem.get("width"))
    h = _parse_float(image_elem.get("height"))
    return w >= canvas_w * 0.9 and h >= canvas_h * 0.9


def _get_or_create_defs(root: ET.Element, ns: str) -> ET.Element:
    """获取或创建 <defs> 元素。"""
    tag = f"{ns}defs" if ns else "defs"
    defs = root.find(tag)
    if defs is None:
        defs = ET.SubElement(root, "defs")
        # 将 defs 移到根元素的第一个位置（背景 rect 之后）
        children = list(root)
        if len(children) > 1:
            root.remove(defs)
            root.insert(1, defs)
    return defs


def _ensure_shadow_filter(root: ET.Element, ns: str) -> str:
    """确保 <defs> 中存在阴影 filter，返回可用的 filter id。"""
    defs = _get_or_create_defs(root, ns)
    filter_tag = f"{ns}filter" if ns else "filter"

    # 检查是否已有 shadow filter
    for f in defs.iter(filter_tag):
        fid = f.get("id", "")
        if "shadow" in fid.lower():
            return fid

    # 没有则创建
    shadow_elem = ET.fromstring(SHADOW_FILTER_XML)
    defs.append(shadow_elem)
    return SHADOW_FILTER_ID


def add_image_cards(tree: ET.ElementTree) -> int:
    """
    为 SVG 中缺少白色底卡的 <image> 元素添加底卡。

    Args:
        tree: 已解析的 ElementTree 对象（会原地修改）。

    Returns:
        添加底卡的数量。
    """
    root = tree.getroot()

    ns = ""
    root_tag = root.tag
    if "}" in root_tag:
        ns = root_tag.split("}")[0] + "}"

    # 获取画布尺寸
    viewbox = root.get("viewBox")
    canvas_w, canvas_h = 1280.0, 720.0
    if viewbox:
        parts = viewbox.split()
        if len(parts) == 4:
            try:
                canvas_w, canvas_h = float(parts[2]), float(parts[3])
            except ValueError:
                pass

    # 收集所有需要处理的 (parent, image_elem) 对
    image_tag = f"{ns}image"
    targets = []

    def _collect(parent: ET.Element):
        for child in parent:
            child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            # 跳过 defs 内的元素
            if child_tag == "defs":
                continue
            if child.tag == image_tag or child_tag == "image":
                targets.append((parent, child))
            _collect(child)

    _collect(root)

    if not targets:
        return 0

    added = 0
    shadow_filter_id = None

    for parent, image_elem in targets:
        # 跳过全屏背景图
        if _is_fullscreen_image(image_elem, canvas_w, canvas_h):
            continue

        # 跳过已有底卡的图片
        if _has_card_backing(image_elem, parent, ns):
            continue

        # 获取或创建阴影 filter
        if shadow_filter_id is None:
            shadow_filter_id = _ensure_shadow_filter(root, ns)

        img_x = _parse_float(image_elem.get("x"))
        img_y = _parse_float(image_elem.get("y"))
        img_w = _parse_float(image_elem.get("width"))
        img_h = _parse_float(image_elem.get("height"))

        # 跳过尺寸异常的图片
        if img_w <= 0 or img_h <= 0:
            continue

        # 创建底卡 rect
        card = ET.Element("rect")
        card.set("x", str(round(img_x - CARD_PADDING, 1)))
        card.set("y", str(round(img_y - CARD_PADDING, 1)))
        card.set("width", str(round(img_w + CARD_PADDING * 2, 1)))
        card.set("height", str(round(img_h + CARD_PADDING * 2, 1)))
        card.set("rx", str(CARD_RX))
        card.set("fill", CARD_FILL)
        card.set("filter", f"url(#{shadow_filter_id})")

        # 插入到 image 之前
        children = list(parent)
        idx = children.index(image_elem)
        parent.insert(idx, card)

        added += 1
        logger.debug(f"   -> Added white card backing for <image> at ({img_x}, {img_y})")

    return added
