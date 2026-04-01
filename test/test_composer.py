"""
测试 agents/composer 模块（svg_generator + svg_runner）。
使用 test_slide_planner_output/slide_04_expansion.md 作为详细描述，
调用 generate_slide_svg 生成 SVG，再经 execute_svg 验证保存，
最后用 merge_svgs_to_pptx 转成 PPTX。
产物输出到 test/test_composer_output/。
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.composer.svg_generator import generate_slide_svg
from agents.composer.svg_runner import execute_svg, merge_svgs_to_pptx
from utils.llm import LLMConfig


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    plan_path = PROJECT_ROOT / "test" / "test_planner_output" / "plan" / "presentation_plan_v0.json"
    detail_path = PROJECT_ROOT / "test" / "test_slide_planner_output" / "slide_04_expansion.md"
    style_path = PROJECT_ROOT / "test" / "test_style_analyst_output" / "style" / "style_protocol_v0.md"
    output_dir = PROJECT_ROOT / "test" / "test_composer_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(plan_path, "r", encoding="utf-8") as f:
        presentation_plan = json.load(f)

    slide_plan = next((s for s in presentation_plan if s.get("slide_page") == 4), None)
    if slide_plan is None:
        print("[Test] FAILED: slide_page 4 not found.")
        sys.exit(1)

    with open(detail_path, "r", encoding="utf-8") as f:
        slide_detail = f.read()

    with open(style_path, "r", encoding="utf-8") as f:
        style_protocol = f.read()

    llm_config: LLMConfig = {
        "model_name": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }

    total_pages = len(presentation_plan)
    print(f"[Test] Generating SVG for slide {slide_plan['slide_page']} / {total_pages}")
    print(f"[Test] Output dir: {output_dir}")

    # 1. 生成 SVG
    svg_code = generate_slide_svg(
        slide_plan=slide_plan,
        style_protocol=style_protocol,
        llm_config=llm_config,
        total_pages=total_pages,
        slide_detail=slide_detail,
    )

    if not svg_code:
        print("[Test] FAILED: SVG generation returned empty result.")
        sys.exit(1)

    print(f"[Test] SVG generated ({len(svg_code)} chars).")

    # 2. 验证并保存 SVG
    svg_path = output_dir / "slide_04.svg"
    success, error = execute_svg(svg_code, str(svg_path))
    if not success:
        print(f"[Test] FAILED: SVG execution failed: {error}")
        sys.exit(1)

    print(f"[Test] SVG validated and saved: {svg_path}")

    # 3. 转换为 PPTX
    pptx_path = output_dir / "slide_04.pptx"
    result = merge_svgs_to_pptx([str(svg_path)], str(pptx_path))
    if not result:
        print("[Test] FAILED: PPTX conversion failed.")
        sys.exit(1)

    print(f"[Test] PPTX created: {pptx_path}")
    print("[Test] SUCCESS.")


if __name__ == "__main__":
    main()
