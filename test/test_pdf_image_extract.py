"""
Test: extract images from assets/paper.pdf using pypdfium2,
then auto-rotate via Pillow's ImageOps.exif_transpose.

Run with:
    S:/dev/miniconda3/envs/slides-gen/python.exe test/test_pdf_image_extract.py
"""

import io
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageOps

PDF_PATH = Path("assets/paper.pdf")
OUT_DIR = Path("output/test_pdf_images")
OUT_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_TYPE = pdfium.raw.FPDF_PAGEOBJ_IMAGE

pdf = pdfium.PdfDocument(str(PDF_PATH))
print(f"PDF pages: {len(pdf)}")

extracted = []

for page_idx in range(len(pdf)):
    page = pdf[page_idx]
    img_objs = list(page.get_objects(filter=[IMAGE_TYPE]))
    if not img_objs:
        continue

    for local_idx, img_obj in enumerate(img_objs):
        try:
            buf = io.BytesIO()
            img_obj.extract(buf)
            buf.seek(0)

            pil_img = Image.open(buf)
            pil_img.load()  # fully decode

            w_orig, h_orig = pil_img.size
            mode_orig = pil_img.mode

            # --- EXIF 自动旋转 ---
            rotated = ImageOps.exif_transpose(pil_img)

            w_rot, h_rot = rotated.size
            was_rotated = (w_orig, h_orig) != (w_rot, h_rot)

            # 保存为 PNG
            filename = f"page{page_idx+1:02d}_img{local_idx+1:02d}.png"
            out_path = OUT_DIR / filename
            rotated.convert("RGB").save(out_path)

            rot_tag = " [ROTATED]" if was_rotated else ""
            print(f"  {filename}  {mode_orig}  {w_orig}x{h_orig} -> {w_rot}x{h_rot}{rot_tag}")

            extracted.append({
                "page": page_idx + 1,
                "original_size": (w_orig, h_orig),
                "final_size": (w_rot, h_rot),
                "was_rotated": was_rotated,
                "path": str(out_path),
            })

        except Exception as e:
            print(f"  page {page_idx+1} obj {local_idx+1} skip: {e}")

pdf.close()

print(f"\nTotal images extracted: {len(extracted)}")
rotated_count = sum(1 for i in extracted if i["was_rotated"])
print(f"Auto-rotated via EXIF: {rotated_count}")
print(f"Output dir: {OUT_DIR.resolve()}")
