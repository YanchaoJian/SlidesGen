"""
测试 agent/designer/style_analyzer.py 的风格提取功能。

使用方法:
    python test/test_style_analyzer.py
    python test/test_style_analyzer.py --image assets/ref-style-img.png
    python test/test_style_analyzer.py --provider ms   # 使用 ModelScope API
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

from agents.style_analyst.analyzer import analyze_style
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
    """从 .env 加载指定 provider 的 LLM 配置。"""
    load_dotenv(ROOT_DIR / ".env")

    prov = PROVIDERS.get(provider)
    if not prov:
        raise ValueError(f"未知 provider: {provider}, 可选: {list(PROVIDERS.keys())}")

    base_url = os.getenv(prov["base_url_env"])
    api_key = os.getenv(prov["api_key_env"])
    model = os.getenv(prov["model_env"])

    missing = []
    if not base_url:
        missing.append(prov["base_url_env"])
    if not api_key:
        missing.append(prov["api_key_env"])
    if not model:
        missing.append(prov["model_env"])
    if missing:
        raise ValueError(f".env 缺少以下配置: {missing}")

    return LLMConfig(model_name=model, api_key=api_key, base_url=base_url)


def parse_args():
    parser = argparse.ArgumentParser(description="测试风格提取模块")
    parser.add_argument(
        "--image",
        default="assets/ref-style-img.png",
        help="参考风格图片路径 (相对项目根目录)",
    )
    parser.add_argument(
        "--output_dir",
        default="test/style_analyzer",
        help="输出目录 (相对项目根目录)",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=list(PROVIDERS.keys()),
        help="API provider (default: openai)",
    )
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
    logger.info(f"Image: {image_path}")
    logger.info(f"Output: {output_dir}")

    # ── 测试 1: 首次风格提取 ─────────────────────────────────
    print("\n" + "=" * 60)
    print("测试 1: 首次风格提取 (analyze_style)")
    print("=" * 60)

    result = analyze_style(
        style_image_path=image_path,
        output_dir=output_dir,
        llm_config=llm_config,
    )

    if result is None:
        logger.error("❌ 测试 1 失败: analyze_style 返回 None")
        sys.exit(1)

    assert isinstance(result, str), f"返回类型应为 str, 实际: {type(result)}"
    assert len(result) > 100, f"返回内容过短 ({len(result)} chars), 可能不完整"

    print(f"\n✅ 测试 1 通过! 返回 {len(result)} 字符的风格描述")
    print("-" * 60)
    print(result[:500] + ("..." if len(result) > 500 else ""))
    print("-" * 60)

    # 检查输出文件
    saved_path = os.path.join(output_dir, "style", "style_protocol_v0.md")
    assert os.path.exists(saved_path), f"输出文件未生成: {saved_path}"
    logger.info(f"✅ 输出文件已保存: {saved_path}")

    # ── 测试 2: 基于反馈的迭代优化 ─────────────────────────────
    print("\n" + "=" * 60)
    print("测试 2: 基于审查反馈的风格描述优化 (refinement)")
    print("=" * 60)

    mock_critique = (
        "Primary color is too bright, suggest adjusting from #3366FF to #1A3A5C. "
        "Top margin (0.5 inches) is too small, increase to 1.2 inches to avoid collision with header stripe."
    )

    refined_result = analyze_style(
        style_image_path=image_path,
        output_dir=output_dir,
        llm_config=llm_config,
        previous_protocol=result,
        previous_protocol_critique=mock_critique,
        style_protocol_retry_count=1,
        style_protocol_verified=False,
    )

    if refined_result is None:
        logger.error("❌ 测试 2 失败: refinement 返回 None")
        sys.exit(1)

    assert isinstance(refined_result, str), f"返回类型应为 str, 实际: {type(refined_result)}"

    print(f"\n✅ 测试 2 通过! 返回 {len(refined_result)} 字符的优化风格描述")
    print("-" * 60)
    print(refined_result[:500] + ("..." if len(refined_result) > 500 else ""))
    print("-" * 60)

    refined_path = os.path.join(output_dir, "style", "style_protocol_v1.md")
    assert os.path.exists(refined_path), f"优化输出文件未生成: {refined_path}"
    logger.info(f"✅ 优化输出文件已保存: {refined_path}")

    # ── 总结 ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print(f"   v0: {saved_path}")
    print(f"   v1: {refined_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
