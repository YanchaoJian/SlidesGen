"""
Test: 用 marker 提取 assets/paper.pdf 中的图片，
用多模态模型判断图片方向并旋转，保存结果到 output/test_multimodal_rotate/。

核心策略：将原图旋转成 0°/90°/180°/270° 四个版本拼成 2x2 网格，
让模型一次性对比选出文字方向正确的那张，避免单张判断不稳定的问题。

Run with:
    S:/dev/miniconda3/envs/slides-gen/python.exe test/test_multimodal_rotate.py
"""

import os
import sys
import base64
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import logging
logging.basicConfig(level=logging.WARNING)

import time
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from agents.pdf_parser.extractor import ContentExtractor

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

PDF_PATH    = os.path.join(PROJECT_ROOT, "assets", "paper.pdf")
MARKER_PATH = os.path.join(PROJECT_ROOT, "models", "marker")
OUT_DIR     = os.path.join(PROJECT_ROOT, "output", "test_multimodal_rotate")
os.makedirs(OUT_DIR, exist_ok=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ── 四方向网格对比策略 ──

# 标签与对应的 PIL rotate 角度
CANDIDATES = [
    ("A", 0),     # 原图
    ("B", -90),   # 顺时针 90°
    ("C", 180),   # 180°
    ("D", 90),    # 逆时针 90°（= 顺时针 270°）
]

GRID_PROMPT = """\
This image shows four versions (A, B, C, D) of the same figure, each rotated differently.
Only ONE version has the correct orientation where:
- All text and labels read normally (left-to-right, top-to-bottom)
- Charts, axes, and diagrams are upright
- The figure looks natural as it would appear in an academic paper

Look carefully at the text direction in each version. Which single version (A, B, C, or D) has the correct upright orientation?

Reply with EXACTLY one letter: A, B, C, or D."""

LABEL_TO_ANGLE = {label: angle for label, angle in CANDIDATES}


def build_grid(image_obj: Image.Image) -> Image.Image:
    """将图片旋转成 4 个方向，拼成 2x2 网格并标注 A/B/C/D。"""
    variants = []
    for label, angle in CANDIDATES:
        if angle == 0:
            variant = image_obj.copy()
        else:
            variant = image_obj.rotate(angle, expand=True)
        variants.append((label, variant))

    # 统一每个 cell 的尺寸为最大宽高
    max_w = max(v.size[0] for _, v in variants)
    max_h = max(v.size[1] for _, v in variants)

    # 缩放到 cell 内（保持比例），限制单个 cell 最大 800px
    cell_size = min(max(max_w, max_h), 800)
    padding = 10
    label_h = 40  # 标签区域高度

    cells = []
    for label, variant in variants:
        # 缩放到 cell_size 内
        ratio = min(cell_size / variant.size[0], cell_size / variant.size[1])
        if ratio < 1:
            new_size = (int(variant.size[0] * ratio), int(variant.size[1] * ratio))
            variant = variant.resize(new_size, Image.LANCZOS)

        # 创建带标签的 cell
        cw, ch = cell_size + 2 * padding, cell_size + 2 * padding + label_h
        cell = Image.new("RGB", (cw, ch), "white")

        # 居中粘贴图片
        offset_x = (cell_size - variant.size[0]) // 2 + padding
        offset_y = (cell_size - variant.size[1]) // 2 + padding + label_h
        cell.paste(variant, (offset_x, offset_y))

        # 画标签
        draw = ImageDraw.Draw(cell)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except OSError:
            font = ImageFont.load_default()
        draw.text((cw // 2 - 10, 5), label, fill="red", font=font)

        cells.append(cell)

    # 拼成 2x2
    grid_w = cells[0].size[0] * 2
    grid_h = cells[0].size[1] * 2
    grid = Image.new("RGB", (grid_w, grid_h), "white")
    grid.paste(cells[0], (0, 0))
    grid.paste(cells[1], (cells[0].size[0], 0))
    grid.paste(cells[2], (0, cells[0].size[1]))
    grid.paste(cells[3], (cells[0].size[0], cells[0].size[1]))

    return grid


def check_and_fix_orientation(image_obj: Image.Image, client: OpenAI, filename: str = "") -> tuple[Image.Image, str]:
    """构建 4 方向网格图，让模型选出正确方向。"""
    grid = build_grid(image_obj)

    # 保存网格图用于调试
    if filename:
        grid.save(os.path.join(OUT_DIR, f"grid_{filename}"), "JPEG")

    buf = io.BytesIO()
    grid.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": GRID_PROMPT}
            ]
        }],
        max_tokens=10,
    )
    answer = response.choices[0].message.content.strip().strip("'\"").upper()

    # 提取第一个有效字母
    choice = None
    for ch in answer:
        if ch in LABEL_TO_ANGLE:
            choice = ch
            break

    if choice is None or choice == "A":
        return image_obj, f"A(0°)"

    angle = LABEL_TO_ANGLE[choice]
    return image_obj.rotate(angle, expand=True), f"{choice}({angle}°)"


# ── Marker 提取 ──
extractor = ContentExtractor(PDF_PATH, MARKER_PATH, OUT_DIR)
device = extractor.device
print(f"Device: {device}")
print(f"Extracting: {PDF_PATH}\n")

model_lst = create_model_dict(device=device)
converter = PdfConverter(artifact_dict=model_lst)

t0 = time.time()
rendered = converter(PDF_PATH)
print(f"Marker finished in {time.time()-t0:.1f}s\n")

_, _, images = text_from_rendered(rendered)
print(f"Images found by marker: {len(images)}\n")

# ── 逐张图片用网格对比判断方向 ──
for filename, image_obj in images.items():
    w, h = image_obj.size
    print(f"  {filename}  ({w}x{h})  ", end="", flush=True)

    t1 = time.time()
    rotated, action = check_and_fix_orientation(image_obj, client, filename)
    elapsed = time.time() - t1

    rw, rh = rotated.size
    print(f"-> {action}  ({rw}x{rh})  [{elapsed:.1f}s]")

    image_obj.save(os.path.join(OUT_DIR, f"orig_{filename}"), "JPEG")
    rotated.save(os.path.join(OUT_DIR, f"fixed_{filename}"), "JPEG")

print(f"\nOutput dir: {OUT_DIR}")
