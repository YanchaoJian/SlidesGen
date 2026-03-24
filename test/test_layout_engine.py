"""
测试 agent/composer/layout_engine.py 的布局指令生成功能。

仅生成第一页的布局描述，使用 test 目录下已有的风格协议和大纲内容。

使用方法:
    python test/test_layout_engine.py

    # 指定大纲文件和风格文件
    python test/test_layout_engine.py \
        --plan_file test/test_slides_planner/plan/presentation_plan_v0.json \
        --style_file test/style_analyzer/style/style_protocol_v1.md

    # 切换 API provider
    python test/test_layout_engine.py --provider ms
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

from agent.composer.layout_engine import generate_layout_directive
from utils.llm_helpers import LLMConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── API 配置预设 ──────────────────────────────────────────────
PROVIDERS = {
    "openai": {
        "base_url_env": "OPENAI_BASE_URL",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
    },
    "ms": {
        "base_url_env": "MS_BASE_URL",
        "api_key_env": "MS_API_KEY",
        "model_env": "MS_MODEL_CODER",
    },
    "awesome": {
        "base_url_env": "AWESOME_BASE_URL",
        "api_key_env": "AWESOME_API_KEY",
        "model_env": "AWESOME_MODEL",
    },
}


def load_llm_config(provider: str) -> LLMConfig:
    load_dotenv(ROOT_DIR / ".env")
    prov = PROVIDERS.get(provider)
    if not prov:
        raise ValueError(f"未知 provider: {provider}, 可选: {list(PROVIDERS.keys())}")

    base_url = os.getenv(prov["base_url_env"])
    api_key = os.getenv(prov["api_key_env"])
    model = os.getenv(prov["model_env"])

    missing = [k for k in ("base_url_env", "api_key_env", "model_env") if not os.getenv(prov[k])]
    if missing:
        raise ValueError(f".env 缺少: {[prov[k] for k in missing]}")

    return LLMConfig(model_name=model, api_key=api_key, base_url=base_url)


def parse_args():
    parser = argparse.ArgumentParser(description="测试布局指令生成模块")
    parser.add_argument(
        "--plan_file",
        default="test/test_slides_planner/plan/presentation_plan_v0.json",
        help="大纲 JSON 文件路径",
    )
    parser.add_argument(
        "--style_file",
        default="test/style_analyzer/style/style_protocol_v1.md",
        help="风格协议文件路径",
    )
    parser.add_argument("--output_dir", default="test/test_layout_engine", help="输出目录")
    parser.add_argument("--provider", default="openai", choices=list(PROVIDERS.keys()))
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = str(ROOT_DIR / args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    llm_config = load_llm_config(args.provider)
    logger.info(f"Provider: {args.provider} | Model: {llm_config['model_name']}")

    # ── 加载风格协议 ──────────────────────────────────────────
    style_path = str(ROOT_DIR / args.style_file) if not os.path.isabs(args.style_file) else args.style_file
    if not os.path.exists(style_path):
        logger.error(f"风格协议文件不存在: {style_path}")
        sys.exit(1)
    with open(style_path, "r", encoding="utf-8") as f:
        style_protocol = f.read()
    logger.info(f"风格协议: {style_path} ({len(style_protocol)} chars)")

    # ── 加载大纲 ──────────────────────────────────────────────
    plan_path = str(ROOT_DIR / args.plan_file) if not os.path.isabs(args.plan_file) else args.plan_file
    if not os.path.exists(plan_path):
        logger.error(f"大纲文件不存在: {plan_path}")
        sys.exit(1)
    with open(plan_path, "r", encoding="utf-8") as f:
        presentation_plan = json.load(f)
    logger.info(f"大纲: {plan_path} ({len(presentation_plan)} 页)")

    # ── 测试: 生成第一页布局指令 ─────────────────────────────
    first_slide = presentation_plan[0]

    print("\n" + "=" * 60)
    print(f"测试: 生成第 {first_slide['slide_page']} 页布局指令")
    print(f"标题: {first_slide['title']}")
    print("=" * 60)

    slide_output_dir = os.path.join(output_dir, f"slide_{first_slide['slide_page']}")

    directive = generate_layout_directive(
        slide_style_protocol=style_protocol,
        slide_content=first_slide,
        llm_config=llm_config,
        output_dir=slide_output_dir,
    )

    if directive is None:
        logger.error("❌ 测试失败: generate_layout_directive 返回 None")
        sys.exit(1)

    assert isinstance(directive, str), f"directive 应为 str, 实际: {type(directive)}"
    assert len(directive) > 50, f"directive 内容过短 ({len(directive)} chars)，可能生成异常"

    # 检查输出文件
    directive_path = os.path.join(slide_output_dir, "directive.txt")
    assert os.path.exists(directive_path), f"指令文件未生成: {directive_path}"

    print(f"\n✅ 测试通过! 布局指令已生成 ({len(directive)} chars)")
    print("-" * 60)
    print(directive)
    print("-" * 60)
    logger.info(f"✅ 输出文件: {directive_path}")


if __name__ == "__main__":
    main()
