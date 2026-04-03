"""
测试 agents/slide_planner/expander.py 的单页大纲扩展效果。
使用 test/test_planner_output/plan/presentation_plan_v0.json 中的 slide_page 4，
以及 test/test_style_analyst_output/style/style_protocol_v0.md 作为设计规范，
产物输出到 test/test_slide_planner_output/。
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.planning.slide_expander import expand_slide_plan
from utils.llm import LLMConfig


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    plan_path = PROJECT_ROOT / "test" / "test_planner_output" / "plan" / "presentation_plan_v0.json"
    style_path = PROJECT_ROOT / "test" / "test_style_analyst_output" / "style" / "style_protocol_v0.md"
    output_dir = PROJECT_ROOT / "test" / "test_slide_planner_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(plan_path, "r", encoding="utf-8") as f:
        presentation_plan = json.load(f)

    slide_plan = next((s for s in presentation_plan if s.get("slide_page") == 4), None)
    if slide_plan is None:
        print("[Test] FAILED: slide_page 4 not found in presentation plan.")
        sys.exit(1)

    with open(style_path, "r", encoding="utf-8") as f:
        style_protocol = f.read()

    llm_config: LLMConfig = {
        "model_name": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }

    print(f"[Test] Expanding slide_page {slide_plan['slide_page']}: '{slide_plan['title']}'")
    print(f"[Test] Style protocol: {style_path} ({len(style_protocol)} chars)")
    print(f"[Test] Output dir: {output_dir}")

    expanded = expand_slide_plan(
        slide_plan=slide_plan,
        style_protocol=style_protocol,
        llm_config=llm_config,
    )

    if expanded is None:
        print("[Test] FAILED: expand_slide_plan returned None.")
        sys.exit(1)

    out_path = output_dir / "slide_04_expansion.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(expanded)

    print(f"[Test] SUCCESS: expansion generated ({len(expanded)} chars).")
    print(f"[Test] Saved to: {out_path}")


if __name__ == "__main__":
    main()
