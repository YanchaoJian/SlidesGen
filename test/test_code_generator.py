"""
测试 agent/composer/code_generator.py 的代码生成功能。

使用 test/test_layout_engine 下已有的 directive.txt 作为布局指令输入，
生成第一页幻灯片的 Python 代码。

使用方法:
    python test/test_code_generator.py

    # 指定 directive 文件
    python test/test_code_generator.py --directive_file test/test_layout_engine/slide_1/directive.txt

    # 切换 API provider
    python test/test_code_generator.py --provider ms
"""

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

from agents.composer.code_generator import generate_slide_code
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
    parser = argparse.ArgumentParser(description="测试代码生成模块")
    parser.add_argument(
        "--directive_file",
        default="test/test_layout_engine/slide_1/directive.txt",
        help="布局指令文件路径",
    )
    parser.add_argument("--output_dir", default="test/test_code_generator", help="输出目录")
    parser.add_argument("--provider", default="openai", choices=list(PROVIDERS.keys()))
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = str(ROOT_DIR / args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    llm_config = load_llm_config(args.provider)
    logger.info(f"Provider: {args.provider} | Model: {llm_config['model_name']}")

    # ── 加载布局指令 ──────────────────────────────────────────
    directive_path = str(ROOT_DIR / args.directive_file) if not os.path.isabs(args.directive_file) else args.directive_file
    if not os.path.exists(directive_path):
        logger.error(f"布局指令文件不存在: {directive_path}")
        logger.error("请先运行 python test/test_layout_engine.py 生成 directive")
        sys.exit(1)
    with open(directive_path, "r", encoding="utf-8") as f:
        code_directive = f.read()
    logger.info(f"布局指令: {directive_path} ({len(code_directive)} chars)")

    # ── 测试 1: 首次生成代码 ─────────────────────────────────
    output_pptx_path = os.path.join(output_dir, "slide_1.pptx")

    print("\n" + "=" * 60)
    print("测试 1: 首次生成幻灯片代码 (Initial Generation)")
    print("=" * 60)

    code = generate_slide_code(
        output_pptx_path=output_pptx_path,
        llm_config=llm_config,
        code_directive=code_directive,
    )

    if code is None:
        logger.error("❌ 测试 1 失败: generate_slide_code 返回 None")
        sys.exit(1)

    assert isinstance(code, str), f"code 应为 str, 实际: {type(code)}"
    assert "import" in code, "生成的代码缺少 import 语句"
    assert "pptx" in code.lower(), "生成的代码未引用 pptx 库"

    # 保存生成的代码
    code_path = os.path.join(output_dir, "slide_1.py")
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n✅ 测试 1 通过! 代码已生成 ({len(code)} chars)")
    print("-" * 60)
    print(code)
    print("-" * 60)
    logger.info(f"✅ 代码文件: {code_path}")

    # ── 测试 2: 代码修复模式 ─────────────────────────────────
    print("\n" + "=" * 60)
    print("测试 2: 代码修复模式 (Code Fixing)")
    print("=" * 60)

    mock_failed_code = code
    mock_error = "TypeError: text_frame.auto_size = True is not valid. Use MSO_AUTO_SIZE enum."

    fixed_code = generate_slide_code(
        output_pptx_path=output_pptx_path,
        llm_config=llm_config,
        code_directive=code_directive,
        failed_code=mock_failed_code,
        error_context=mock_error,
        slide_code_verified=False,
    )

    if fixed_code is None:
        logger.error("❌ 测试 2 失败: 修复模式返回 None")
        sys.exit(1)

    assert isinstance(fixed_code, str), f"fixed_code 应为 str, 实际: {type(fixed_code)}"

    fixed_code_path = os.path.join(output_dir, "slide_1_fixed.py")
    with open(fixed_code_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)

    print(f"\n✅ 测试 2 通过! 修复后代码已生成 ({len(fixed_code)} chars)")
    print("-" * 60)
    print(fixed_code)
    print("-" * 60)
    logger.info(f"✅ 修复代码文件: {fixed_code_path}")

    # ── 总结 ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print(f"   输出目录: {output_dir}")
    print(f"   初始代码: {code_path}")
    print(f"   修复代码: {fixed_code_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
