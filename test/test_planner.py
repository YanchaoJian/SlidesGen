"""
测试 agents/planner 模块。
使用 test/test_pdf_parser_output/raw/pdf-content.json 作为输入，
调用 plan_presentation 生成演示大纲，产物输出到 test/test_planner_output/。
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.ppt_planner.planner import plan_presentation
from utils.llm import LLMConfig


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    pdf_content_path = PROJECT_ROOT / "test" / "test_pdf_parser_output" / "raw" / "pdf-content.json"
    output_dir = PROJECT_ROOT / "test" / "test_planner_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(pdf_content_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    llm_config: LLMConfig = {
        "model_name": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }

    print(f"[Test] Input PDF content: {pdf_content_path}")
    print(f"[Test] Output dir: {output_dir}")
    print(f"[Test] Model: {llm_config['model_name']}")

    paper_main_content, presentation_plan = plan_presentation(
        previous_main_content=None,
        previous_plan=None,
        user_feedback_plan=None,
        presentation_plan_verified=False,
        content=content,
        presentation_plan_retry_count=0,
        output_dir=str(output_dir),
        llm_config=llm_config,
    )

    if presentation_plan is None:
        print("[Test] FAILED: presentation_plan generation failed.")
        sys.exit(1)

    print(f"[Test] SUCCESS: plan generated with {len(presentation_plan)} slides.")
    print(f"  - Main content keys: {list(paper_main_content.keys()) if paper_main_content else 'None'}")
    print(f"  - Plan saved under: {output_dir / 'plan'}")


if __name__ == "__main__":
    main()
