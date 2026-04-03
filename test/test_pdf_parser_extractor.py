"""
测试 agents/pdf_parser 模块（extractor.py + image_orientation.py）。
像实际项目一样调用 extract_pdf，使用 assets/paper.pdf 和真实 API，
产物输出到 test/test_pdf_parser_output/。
"""

import os
import sys
from pathlib import Path

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.perception.pdf_parser.extractor import extract_pdf


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    pdf_path = PROJECT_ROOT / "assets" / "paper.pdf"
    marker_path = PROJECT_ROOT / "models" / "marker"
    output_dir = PROJECT_ROOT / "test" / "test_pdf_parser_output"

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = "gpt-4o"

    print(f"[Test] PDF path: {pdf_path}")
    print(f"[Test] Marker path: {marker_path}")
    print(f"[Test] Output dir: {output_dir}")
    print(f"[Test] API base: {base_url}")

    content, output_file, img_dir = extract_pdf(
        pdf_path=str(pdf_path),
        marker_path=str(marker_path),
        output_dir=str(output_dir),
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
    )

    if content is None:
        print("[Test] FAILED: extract_pdf returned None.")
        sys.exit(1)

    print(f"[Test] SUCCESS: content extracted.")
    print(f"  - Text length: {len(content.get('full_text', ''))}")
    print(f"  - Images: {len(content.get('images', []))}")
    print(f"  - Tables: {len(content.get('tables', []))}")
    print(f"  - Equations: {len(content.get('equations', []))}")
    print(f"  - JSON saved: {output_file}")
    print(f"  - Images dir: {img_dir}")


if __name__ == "__main__":
    main()
