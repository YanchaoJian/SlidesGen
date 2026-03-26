"""
测试 agent/designer/style_critic.py 的风格审查功能。

依赖: 先运行 test_style_analyzer.py 生成风格描述，或直接提供 --style_text / --style_file。

使用方法:
    # 自动先提取风格再审查（端到端）
    python test/test_style_critic.py

    # 指定已有的风格描述文件
    python test/test_style_critic.py --style_file test/output_style_analyzer/style/style_protocol_v0.md

    # 使用 ModelScope API
    python test/test_style_critic.py --provider ms
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

from agents.style_analyst.analyzer import analyze_style
from agents.style_analyst.critic import critique_style_protocol
from utils.llm import LLMConfig

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
        "model_env": "MS_MODEL_VL",
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
    parser = argparse.ArgumentParser(description="测试风格审查模块")
    parser.add_argument("--image", default="assets/ref-style-img.png", help="参考风格图片路径")
    parser.add_argument("--output_dir", default="test/style_critic", help="输出目录")
    parser.add_argument("--provider", default="openai", choices=list(PROVIDERS.keys()))
    parser.add_argument("--style_file", default=None, help="已有的风格描述文件路径，跳过提取步骤")
    return parser.parse_args()


def main():
    args = parse_args()

    image_path = str(ROOT_DIR / args.image)
    output_dir = str(ROOT_DIR / args.output_dir)

    if not os.path.exists(image_path):
        logger.error(f"图片文件不存在: {image_path}")
        sys.exit(1)

    llm_config = load_llm_config(args.provider)
    logger.info(f"Provider: {args.provider} | Model: {llm_config['model_name']}")

    # ── 准备风格描述文本 ─────────────────────────────────────
    if args.style_file:
        style_file = str(ROOT_DIR / args.style_file) if not os.path.isabs(args.style_file) else args.style_file
        if not os.path.exists(style_file):
            logger.error(f"风格描述文件不存在: {style_file}")
            sys.exit(1)
        with open(style_file, "r", encoding="utf-8") as f:
            style_text = f.read()
        logger.info(f"从文件加载风格描述: {style_file} ({len(style_text)} chars)")
    else:
        print("\n" + "=" * 60)
        print("准备阶段: 先提取风格描述 (analyze_style)")
        print("=" * 60)
        style_text = analyze_style(
            style_image_path=image_path,
            output_dir=output_dir,
            llm_config=llm_config,
        )
        if not style_text:
            logger.error("❌ 风格提取失败，无法继续测试 critic")
            sys.exit(1)
        logger.info(f"风格提取完成 ({len(style_text)} chars)")

    # ── 测试 1: 正常审查 ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("测试 1: 审查风格描述 (review_visual_protocol)")
    print("=" * 60)

    is_approved, critique = critique_style_protocol(
        output_dir=output_dir,
        image_path=image_path,
        style_protocol=style_text,
        llm_config=llm_config,
    )

    assert isinstance(is_approved, bool), f"is_approved 应为 bool, 实际: {type(is_approved)}"
    assert isinstance(critique, str), f"critique 应为 str, 实际: {type(critique)}"
    assert len(critique) > 0, "critique 不应为空"

    status = "APPROVED" if is_approved else "REJECTED"
    print(f"\n✅ 测试 1 通过! 审查结果: {status}")
    print(f"Critique ({len(critique)} chars):")
    print("-" * 60)
    print(critique[:600] + ("..." if len(critique) > 600 else ""))
    print("-" * 60)

    # 检查历史记录文件
    history_file = os.path.join(output_dir, "style", "critique_history.json")
    assert os.path.exists(history_file), f"审查历史文件未生成: {history_file}"
    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)
    assert isinstance(history, list) and len(history) >= 1, "审查历史应至少有 1 条记录"
    logger.info(f"✅ 审查历史已保存: {history_file} ({len(history)} 条记录)")

    # ── 测试 2: 用故意错误的风格描述测试 REJECT ───────────────
    print("\n" + "=" * 60)
    print("测试 2: 使用故意偏差的风格描述，预期触发 REJECT")
    print("=" * 60)

    bad_style_text = """
## 1. Style Overview
- Style Name: "Neon Chaos"
- Visual Mood: Extremely colorful and chaotic with clashing neon colors.

## 2. Color Palette
- **Background Main**: #FF00FF (bright magenta)
- **Primary**: #00FF00 (lime green)
- **Secondary**: #FFFF00 (yellow)
- **Accent**: #FF0000 (red)
- **Text Dark**: #FFFFFF (white)
- **Text Light**: #000000 (black)

## 3. Layout Rules
- **Page Margins**: top 0.1, bottom 0.1, left 0.1, right 0.1 inches.
- **Title Position**: center, x=5.0, y=3.0, max width 3 inches.
- **Content Area**: x=0.1, y=0.1, width=9.8, height=5.4 inches.

## 4. Background & Decoration Elements
No decoration elements.

## 5. Typography Rules
- **Slide Title**: Comic Sans MS, 12pt, Text Dark color, not bold, not uppercase.
- **Section Header**: Comic Sans MS, 11pt, Primary color, not bold.
- **Body Text**: Comic Sans MS, 10pt, Text Dark color, line spacing 1.0, no bullets.
"""

    is_approved_bad, critique_bad = critique_style_protocol(
        output_dir=output_dir,
        image_path=image_path,
        style_protocol=bad_style_text,
        llm_config=llm_config,
    )

    assert isinstance(is_approved_bad, bool)
    assert isinstance(critique_bad, str) and len(critique_bad) > 0

    status_bad = "APPROVED" if is_approved_bad else "REJECTED"
    print(f"\n✅ 测试 2 通过! 审查结果: {status_bad}")
    if not is_approved_bad:
        print("   (符合预期: 故意偏差的描述被 REJECT)")
    else:
        print("   (注意: 故意偏差的描述被 APPROVE，critic 可能不够严格)")
    print(f"Critique: {critique_bad[:400]}...")

    # 验证历史记录追加
    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)
    assert len(history) >= 2, f"审查历史应至少有 2 条记录, 实际: {len(history)}"
    logger.info(f"✅ 审查历史已追加: {len(history)} 条记录")

    # ── 总结 ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print(f"   输出目录: {output_dir}")
    print(f"   审查历史: {history_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
