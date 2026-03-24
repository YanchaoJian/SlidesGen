"""测试 agent/parser/pdf_extractor.py 的完整提取功能。"""

import json
import logging
import os
import sys

# 将项目根目录加入 sys.path，以便导入 agent 模块
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from agent.parser.pdf_extractor import extract_content

# 所有路径基于项目根目录
PDF_PATH = os.path.join(PROJECT_ROOT, "assets", "Attention.pdf")
MARKER_PATH = os.path.join(PROJECT_ROOT, "models", "marker")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_extractor")


def main():
    if not os.path.exists(PDF_PATH):
        print(f"PDF not found: {PDF_PATH}")
        sys.exit(1)

    print(f"=== Testing PDF extraction: {PDF_PATH} ===\n")

    content, output_file, img_dir = extract_content(PDF_PATH, MARKER_PATH, OUTPUT_DIR)

    if content is None:
        print("Extraction failed!")
        sys.exit(1)

    # --- full_text ---
    full_text = content["full_text"]
    print(f"[full_text] length: {len(full_text)} chars")
    print(f"[full_text] preview (first 500 chars):\n{full_text[:500]}\n")

    # --- images ---
    images = content["images"]
    print(f"[images] count: {len(images)}")
    for img in images:
        exists = os.path.exists(img["path"])
        print(f"  - caption: {img['caption'][:80] if img['caption'] else '(none)'}")
        print(f"    path: {img['path']}  (exists={exists})")
    print()

    # --- tables ---
    tables = content["tables"]
    print(f"[tables] count: {len(tables)}")
    for i, tbl in enumerate(tables):
        print(f"\n  --- Table {i+1}: {tbl['caption']} ---")
        # 显示前 5 行
        lines = tbl["markdown"].split('\n')
        for line in lines[:5]:
            print(f"    {line}")
        if len(lines) > 5:
            print(f"    ... ({len(lines) - 5} more rows)")
    print()

    # --- equations ---
    equations = content["equations"]
    print(f"[equations] count: {len(equations)}")
    for i, eq in enumerate(equations):
        latex_preview = eq["latex"][:100]
        print(f"  {i+1}. {latex_preview}")
    print()

    # --- saved file ---
    print(f"[output] JSON saved to: {output_file}")
    print(f"[output] Images dir: {img_dir}")

    print("\n=== Test passed ===")


if __name__ == "__main__":
    main()
