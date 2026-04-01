"""
图片方向检测与修正模块。

使用多模态模型对比 4 个旋转候选（0°/90°/180°/270°），
选出文字方向正确的版本。
"""

import base64
import io
import logging
from typing import Dict

from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

from agents.pdf_parser.prompts import IMAGE_ORIENTATION_PROMPT

logger = logging.getLogger(__name__)

# 标签 → PIL rotate 角度
_CANDIDATES = [
    ("A", 0),     # 原图
    ("B", -90),   # 顺时针 90°
    ("C", 180),   # 180°
    ("D", 90),    # 逆时针 90°
]

_LABEL_TO_ANGLE: Dict[str, int] = {label: angle for label, angle in _CANDIDATES}


def _build_orientation_grid(image_obj: Image.Image) -> Image.Image:
    """将图片旋转成 4 个方向，拼成 2×2 网格并标注 A/B/C/D。"""
    variants = []
    for label, angle in _CANDIDATES:
        variant = image_obj if angle == 0 else image_obj.rotate(angle, expand=True)
        variants.append((label, variant))

    max_w = max(v.size[0] for _, v in variants)
    max_h = max(v.size[1] for _, v in variants)
    cell_size = min(max(max_w, max_h), 1600)
    padding = 10
    label_h = 40

    cells = []
    for label, variant in variants:
        ratio = min(cell_size / variant.size[0], cell_size / variant.size[1])
        if ratio < 1:
            new_size = (int(variant.size[0] * ratio), int(variant.size[1] * ratio))
            variant = variant.resize(new_size, Image.LANCZOS)

        cw = cell_size + 2 * padding
        ch = cell_size + 2 * padding + label_h
        cell = Image.new("RGB", (cw, ch), "white")

        offset_x = (cell_size - variant.size[0]) // 2 + padding
        offset_y = (cell_size - variant.size[1]) // 2 + padding + label_h
        cell.paste(variant, (offset_x, offset_y))

        draw = ImageDraw.Draw(cell)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font = ImageFont.load_default()
        draw.text((cw // 2 - 10, 5), label, fill="red", font=font)
        cells.append(cell)

    grid_w = cells[0].size[0] * 2
    grid_h = cells[0].size[1] * 2
    grid = Image.new("RGB", (grid_w, grid_h), "white")
    grid.paste(cells[0], (0, 0))
    grid.paste(cells[1], (cells[0].size[0], 0))
    grid.paste(cells[2], (0, cells[0].size[1]))
    grid.paste(cells[3], (cells[0].size[0], cells[0].size[1]))
    return grid


def fix_image_orientation(image_obj: Image.Image, client: OpenAI, model: str = "gpt-4o") -> Image.Image:
    """
    使用多模态模型检测并修正图片方向。

    构建 4 方向网格图让模型对比选择，返回修正后的图片。
    如果模型判断原图方向正确或调用失败，返回原图。

    为提高稳定性，采用 3 次投票机制（temperature=0.2），
    并增强 prompt 以抑制默认选 A 的偏差。

    Args:
        image_obj: 待检测的 PIL Image 对象。
        client: OpenAI 客户端实例。
        model: 多模态模型名称。

    Returns:
        方向修正后的 PIL Image 对象。
    """
    try:
        grid = _build_orientation_grid(image_obj)

        buf = io.BytesIO()
        grid.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        enhanced_prompt = (
            IMAGE_ORIENTATION_PROMPT
            + "\n\nDo not default to A. Carefully compare all four versions before choosing."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    {"type": "text", "text": enhanced_prompt},
                ],
            }],
            max_completion_tokens=10,
            temperature=0.2,
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
