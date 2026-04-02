"""
测试 Slide 生成-审查-重生成完整流程。
使用 test_slide_planner_output/slide_04_expansion.md 作为输入，
依次调用：生成 SVG → 验证保存 → 转 PPTX → 转图片 → 视觉评判 → 若未通过则利用 critique 重生成 SVG → 再次评判。
产物输出到 test/test_slide_review_regen_output/。
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.slide_composer.svg_generator import generate_slide_svg
from utils.svg_validator import execute_svg
from utils.pptx_merger import merge_svgs_to_pptx
from utils.pptx_imaging import pptx_to_images
from agents.slide_reviewer.critic import evaluate_and_critique_slide
from utils.llm import LLMConfig


def build_llm_config() -> LLMConfig:
    return {
        "model_name": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    llm_config = build_llm_config()

    # 输入素材
    plan_path = PROJECT_ROOT / "test" / "test_planner_output" / "plan" / "presentation_plan_v0.json"
    detail_path = PROJECT_ROOT / "test" / "test_slide_planner_output" / "slide_04_expansion.md"
    style_path = PROJECT_ROOT / "test" / "test_style_analyst_output" / "style" / "style_protocol_v0.md"

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

    output_dir = PROJECT_ROOT / "test" / "test_slide_review_regen_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    total_pages = len(presentation_plan)
    print(f"[Test] Slide page: 4 / {total_pages}")
    print(f"[Test] Output dir: {output_dir}")

    # 初始状态
    svg_code = None
    failed_svg = None
    error_context = None
    max_iterations = 2

    for iteration in range(max_iterations):
        print(f"\n========== Iteration {iteration} ==========")

        # 1. 生成 SVG
        svg_code = generate_slide_svg(
            slide_plan=slide_plan,
            style_protocol=style_protocol,
            llm_config=llm_config,
            total_pages=total_pages,
            slide_detail=slide_detail,
            failed_svg=failed_svg,
            error_context=error_context,
        )

        if not svg_code:
            print(f"[Test] FAILED: SVG generation returned empty at iteration {iteration}.")
            sys.exit(1)

        print(f"[Test] SVG generated ({len(svg_code)} chars).")

        # 2. 验证并保存 SVG
        svg_path = output_dir / f"slide_04_v{iteration}.svg"
        success, error = execute_svg(svg_code, str(svg_path))
        if not success:
            print(f"[Test] SVG execution failed at iteration {iteration}: {error}")
            failed_svg = svg_code
            error_context = error or "SVG execution failed"
            continue

        print(f"[Test] SVG saved: {svg_path}")

        # 3. 转 PPTX
        pptx_path = output_dir / f"slide_04_v{iteration}.pptx"
        result = merge_svgs_to_pptx([str(svg_path)], str(pptx_path))
        if not result:
            print(f"[Test] FAILED: PPTX conversion failed at iteration {iteration}.")
            sys.exit(1)

        print(f"[Test] PPTX created: {pptx_path}")

        # 4. 转图片（用于视觉评判）
        img_dir = output_dir / f"images_v{iteration}"
        img_dir.mkdir(parents=True, exist_ok=True)
        image_count = pptx_to_images(str(pptx_path), str(img_dir), dpi=150)
        if image_count == 0:
            print(f"[Test] WARNING: PPTX to image conversion returned 0 images at iteration {iteration}.")
        else:
            print(f"[Test] Generated {image_count} image(s) in {img_dir}")

        # 5. 视觉评判
        critique = evaluate_and_critique_slide(
            slide_code=svg_code,
            svg_path=str(svg_path),
            slide_style_protocol=style_protocol,
            llm_config=llm_config,
        )

        if critique is None:
            print(f"[Test] [PASS] Slide passed visual critique at iteration {iteration}.")
            print("[Test] SUCCESS.")
            sys.exit(0)
        else:
            print(f"[Test] [REVISE] Critique received at iteration {iteration}:")
            print(critique)
            failed_svg = svg_code
            error_context = critique

    print(f"\n[Test] Reached max iterations ({max_iterations}). Final critique was not resolved.")
    print("[Test] Done (with remaining issues).")


if __name__ == "__main__":
    main()
