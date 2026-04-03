"""
测试 agents/style_analyst 模块（analyzer + critic）。
使用 assets/ref-style-img.png 作为参考图，调用 analyze_style 生成风格协议，
再调用 critique_style_protocol 进行审查。
产物输出到 test/test_style_analyst_output/。
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from agents.perception.style_analyst.analyzer import analyze_style
from agents.perception.style_analyst.critic import critique_style_protocol
from utils.llm import LLMConfig


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    image_path = PROJECT_ROOT / "assets" / "ref-style-img.png"
    output_dir = PROJECT_ROOT / "test" / "test_style_analyst_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    llm_config: LLMConfig = {
        "model_name": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }

    print(f"[Test] Style image: {image_path}")
    print(f"[Test] Output dir: {output_dir}")

    # 1. 风格分析
    style_protocol = analyze_style(
        style_image_path=str(image_path),
        output_dir=str(output_dir),
        llm_config=llm_config,
        previous_protocol=None,
        previous_protocol_critique=None,
        style_protocol_retry_count=0,
        style_protocol_verified=False,
    )

    if style_protocol is None:
        print("[Test] FAILED: style analysis returned None.")
        sys.exit(1)

    print(f"[Test] Style protocol generated ({len(style_protocol)} chars).")

    # 2. 风格审查
    is_approved, critique = critique_style_protocol(
        output_dir=str(output_dir),
        image_path=str(image_path),
        style_protocol=style_protocol,
        llm_config=llm_config,
    )

    status = "APPROVED" if is_approved else "REJECTED"
    print(f"[Test] Style critique result: {status}")
    print(f"[Test] Critique: {critique[:200]}...")
    print(f"[Test] Outputs saved under: {output_dir / 'style'}")


if __name__ == "__main__":
    main()
