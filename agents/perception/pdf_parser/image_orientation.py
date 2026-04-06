"""
图片方向检测与修正模块。

学术论文 PDF 中的图片只有两种状态：
  - 正立（A，不需旋转）
  - 逆时针旋转 90° 倒放（需顺时针 90° 修正，即 B）

因此只构造 A/B 两个候选，让多模态模型二选一。
候选拼接时保留原始分辨率，避免模型看不清文字。
"""

import base64
import io
import logging
from typing import Dict

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

from agents.perception.pdf_parser.prompts import IMAGE_ORIENTATION_PROMPT

logger = logging.getLogger(__name__)

# 标签 → PIL rotate 角度
# A: 原图；B: 顺时针 90°（修正逆时针倒放的情况）
_CANDIDATES = [
    ("A", 0),
    ("B", -90),
]

_LABEL_TO_ANGLE: Dict[str, int] = {label: angle for label, angle in _CANDIDATES}


def _build_orientation_pair(image_obj: Image.Image) -> Image.Image:
    """
    将图片构造成 A（原图）和 B（顺时针 90°）两个候选，
    横向并排拼成一张图并标注 A/B。

    保留原始像素分辨率，不缩放，以确保文字可读。
    """
    variants = []
    for label, angle in _CANDIDATES:
        variant = image_obj if angle == 0 else image_obj.rotate(angle, expand=True)
        variants.append((label, variant))

    # 以两个候选中最大的宽/高作为 cell 尺寸，不做上限截断
    cell_w = max(v.size[0] for _, v in variants)
    cell_h = max(v.size[1] for _, v in variants)
    padding = 20
    label_h = 50

    cells = []
    for label, variant in variants:
        cw = cell_w + 2 * padding
        ch = cell_h + 2 * padding + label_h
        cell = Image.new("RGB", (cw, ch), "white")

        offset_x = (cell_w - variant.size[0]) // 2 + padding
        offset_y = (cell_h - variant.size[1]) // 2 + padding + label_h
        cell.paste(variant, (offset_x, offset_y))

        draw = ImageDraw.Draw(cell)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except OSError:
            font = ImageFont.load_default()
        draw.text((cw // 2 - 12, 8), label, fill="red", font=font)
        cells.append(cell)

    # 1×2 横向并排
    pair_w = cells[0].size[0] + cells[1].size[0]
    pair_h = max(cells[0].size[1], cells[1].size[1])
    pair = Image.new("RGB", (pair_w, pair_h), "white")
    pair.paste(cells[0], (0, 0))
    pair.paste(cells[1], (cells[0].size[0], 0))
    return pair


def fix_image_orientation(image_obj: Image.Image, client: OpenAI, model: str = "gpt-4o") -> Image.Image:
    """
    使用多模态模型检测并修正图片方向（二选一版本）。

    构造 A（原图）/ B（顺时针 90°）两个候选并排拼成一张图，
    让模型选出正确方向。单次调用 + temperature=0，追求确定性。

    Args:
        image_obj: 待检测的 PIL Image 对象。
        client: OpenAI 客户端实例。
        model: 多模态模型名称。

    Returns:
        方向修正后的 PIL Image 对象。若模型判断原图正确或调用失败，返回原图。
    """
    try:
        pair = _build_orientation_pair(image_obj)

        buf = io.BytesIO()
        # 用 PNG 保留完整分辨率和清晰度，JPEG 在小字上会失真
        pair.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": IMAGE_ORIENTATION_PROMPT},
                ],
            }],
            max_completion_tokens=5,
            temperature=0,
        )
        answer = response.choices[0].message.content.strip().strip("'\"").upper()

        choice = next((ch for ch in answer if ch in _LABEL_TO_ANGLE), None)

        if choice is None or choice == "A":
            logger.debug("Image orientation: ok (no rotation needed)")
            return image_obj

        angle = _LABEL_TO_ANGLE[choice]
        logger.info(f"Image orientation: {choice} (rotate {angle}°)")
        return image_obj.rotate(angle, expand=True)

    except Exception as e:
        logger.warning(f"Orientation detection failed, keeping original: {e}")
        return image_obj
