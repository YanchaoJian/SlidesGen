"""
Test: 验证 SVG → PPTX 转换管线能正常运行。

使用一个简单的 960×540 SVG（背景 + 圆角矩形 + 中文标题 + 正文），
调用 svg_converter 包生成 PPTX，检查文件是否成功创建且可被 python-pptx 打开。

Run with:
    S:/dev/miniconda3/envs/slides-gen/python.exe test/test_svg_to_pptx.py
"""

import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from agents.composer.svg_converter import create_pptx_with_native_svg

TEST_SVG = """\
<svg width="960" height="540" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="960" height="540" fill="#1a1a2e"/>
  <rect x="60" y="80" width="840" height="80" rx="8" fill="#16213e"/>
  <text x="480" y="132" font-size="36" fill="#e94560" text-anchor="middle" font-weight="bold">测试标题</text>
  <text x="480" y="300" font-size="20" fill="#ffffff" text-anchor="middle">这是一段正文内容</text>
</svg>
"""

OUT_DIR = os.path.join(PROJECT_ROOT, "output", "test_svg_to_pptx")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    # 1. 将 SVG 字符串写入临时文件
    svg_path = os.path.join(OUT_DIR, "test_slide.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(TEST_SVG)
    print(f"[1/3] SVG written: {svg_path}")

    # 2. 调用转换
    output_pptx = os.path.join(OUT_DIR, "test_output.pptx")
    print(f"[2/3] Converting SVG -> PPTX ...")
    create_pptx_with_native_svg(
        svg_files=[Path(svg_path)],
        output_path=Path(output_pptx),
        canvas_format="ppt169",
        verbose=True,
        use_native_shapes=True,
    )

    # 3. 验证
    if not os.path.exists(output_pptx):
        print("FAIL: PPTX file was not created.")
        sys.exit(1)

    file_size = os.path.getsize(output_pptx)
    print(f"[3/3] PPTX created: {output_pptx}  ({file_size:,} bytes)")

    # 用 python-pptx 打开验证
    from pptx import Presentation
    prs = Presentation(output_pptx)
    slide_count = len(prs.slides)
    print(f"      Slides: {slide_count}")
    assert slide_count == 1, f"Expected 1 slide, got {slide_count}"

    print("\nPASS: SVG -> PPTX conversion works correctly.")


if __name__ == "__main__":
    main()
