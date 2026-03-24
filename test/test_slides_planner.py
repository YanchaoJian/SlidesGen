"""
测试 agent/planner/slides_planner.py 的大纲规划功能。

使用方法:
    # 使用已有的 base_content.json（跳过 PDF 提取）
    python test/test_slides_planner.py --content_file test/test_extractor/raw/base_content.json

    # 从 PDF 提取内容后规划（需要 marker 模型）
    python test/test_slides_planner.py --pdf assets/paper.pdf --marker_path models/marker

    # 切换 API provider
    python test/test_slides_planner.py --content_file output/0116_2040/raw/base_content.json --provider ms
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

from agent.planner.slides_planner import generate_presentation_plan
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
    parser = argparse.ArgumentParser(description="测试大纲规划模块")
    parser.add_argument("--content_file", default=None, help="已有的 base_content.json 路径（跳过 PDF 提取）")
    parser.add_argument("--pdf", default=None, help="PDF 文件路径（需要 --marker_path）")
    parser.add_argument("--marker_path", default="models/marker", help="Marker 模型路径")
    parser.add_argument("--output_dir", default="test/test_slides_planner", help="输出目录")
    parser.add_argument("--provider", default="openai", choices=list(PROVIDERS.keys()))
    return parser.parse_args()


def load_content(args) -> dict:
    """加载或提取 PDF 内容"""
    if args.content_file:
        content_path = str(ROOT_DIR / args.content_file) if not os.path.isabs(args.content_file) else args.content_file
        if not os.path.exists(content_path):
            logger.error(f"内容文件不存在: {content_path}")
            sys.exit(1)
        with open(content_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        logger.info(f"从文件加载内容: {content_path}")
        # 确保必要字段存在
        content.setdefault("tables", [])
        content.setdefault("equations", [])
        content.setdefault("images", [])
        return content

    if args.pdf:
        pdf_path = str(ROOT_DIR / args.pdf) if not os.path.isabs(args.pdf) else args.pdf
        marker_path = str(ROOT_DIR / args.marker_path) if not os.path.isabs(args.marker_path) else args.marker_path
        if not os.path.exists(pdf_path):
            logger.error(f"PDF 文件不存在: {pdf_path}")
            sys.exit(1)
        logger.info(f"从 PDF 提取内容: {pdf_path}")
        from agent.parser.pdf_extractor import extract_content
        output_dir = str(ROOT_DIR / args.output_dir)
        base_content, _, _ = extract_content(pdf_path=pdf_path, marker_path=marker_path, output_dir=output_dir)
        if not base_content:
            logger.error("PDF 内容提取失败")
            sys.exit(1)
        return base_content

    logger.error("必须指定 --content_file 或 --pdf")
    sys.exit(1)


def main():
    args = parse_args()
    output_dir = str(ROOT_DIR / args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    llm_config = load_llm_config(args.provider)
    logger.info(f"Provider: {args.provider} | Model: {llm_config['model_name']}")

    content = load_content(args)
    logger.info(f"内容概览: full_text={len(content.get('full_text', ''))} chars, "
                f"images={len(content.get('images', []))}, "
                f"tables={len(content.get('tables', []))}, "
                f"equations={len(content.get('equations', []))}")

    # ── 测试 1: 首次生成大纲 ─────────────────────────────────
    print("\n" + "=" * 60)
    print("测试 1: 首次生成演示大纲 (generate_presentation_plan)")
    print("=" * 60)

    result = generate_presentation_plan(
        previous_main_content=None,
        previous_plan=None,
        user_feedback_plan=None,
        presentation_plan_verified=False,
        content=content,
        presentation_plan_retry_count=0,
        output_dir=output_dir,
        llm_config=llm_config,
    )

    if result is None or result == (None, None):
        logger.error("❌ 测试 1 失败: generate_presentation_plan 返回 None")
        sys.exit(1)

    paper_main_content, presentation_plan = result

    assert paper_main_content is not None, "paper_main_content 不应为 None"
    assert isinstance(paper_main_content, dict), f"paper_main_content 应为 dict, 实际: {type(paper_main_content)}"

    if presentation_plan is None:
        logger.error("❌ 测试 1 失败: presentation_plan 为 None（内容提取成功但大纲规划失败）")
        sys.exit(1)

    assert isinstance(presentation_plan, list), f"presentation_plan 应为 list, 实际: {type(presentation_plan)}"
    assert len(presentation_plan) >= 3, f"大纲至少应有 3 页, 实际: {len(presentation_plan)}"

    # 验证每页结构
    for i, slide in enumerate(presentation_plan):
        assert "slide_page" in slide, f"第 {i+1} 页缺少 slide_page"
        assert "title" in slide, f"第 {i+1} 页缺少 title"
        assert "content" in slide, f"第 {i+1} 页缺少 content"

    print(f"\n✅ 测试 1 通过! 生成 {len(presentation_plan)} 页大纲")
    print("-" * 60)
    for slide in presentation_plan:
        fig = "📊" if slide.get("includes_figure") else "  "
        tbl = "📋" if slide.get("includes_table") else "  "
        eq = "📐" if slide.get("includes_equation") else "  "
        print(f"  Slide {slide['slide_page']:2d} {fig}{tbl}{eq} {slide['title']}")
    print("-" * 60)

    # 检查输出文件
    plan_path = os.path.join(output_dir, "plan", "presentation_plan_v0.json")
    main_content_path = os.path.join(output_dir, "plan", "paper_main_content.json")
    assert os.path.exists(plan_path), f"大纲文件未生成: {plan_path}"
    assert os.path.exists(main_content_path), f"主内容文件未生成: {main_content_path}"
    logger.info(f"✅ 输出文件: {plan_path}")
    logger.info(f"✅ 输出文件: {main_content_path}")

    # ── 测试 2: 基于反馈的迭代修改 ─────────────────────────────
    print("\n" + "=" * 60)
    print("测试 2: 基于用户反馈修改大纲 (refinement)")
    print("=" * 60)

    mock_feedback = (
        "1. 第2页背景介绍太笼统，需要加入具体的数据来说明领域的重要性。\n"
        "2. 方法部分（第4-6页）需要拆分得更细，每个创新点单独一页。\n"
        "3. 缺少消融实验的页面，请在实验结果后增加。"
    )

    refined_result = generate_presentation_plan(
        previous_main_content=paper_main_content,
        previous_plan=presentation_plan,
        user_feedback_plan=mock_feedback,
        presentation_plan_verified=False,
        content=content,
        presentation_plan_retry_count=1,
        output_dir=output_dir,
        llm_config=llm_config,
    )

    if refined_result is None or refined_result == (None, None):
        logger.error("❌ 测试 2 失败: refinement 返回 None")
        sys.exit(1)

    _, refined_plan = refined_result

    if refined_plan is None:
        logger.error("❌ 测试 2 失败: refined_plan 为 None")
        sys.exit(1)

    assert isinstance(refined_plan, list), f"refined_plan 应为 list, 实际: {type(refined_plan)}"

    print(f"\n✅ 测试 2 通过! 修改后 {len(refined_plan)} 页大纲 (原 {len(presentation_plan)} 页)")
    print("-" * 60)
    for slide in refined_plan:
        fig = "📊" if slide.get("includes_figure") else "  "
        tbl = "📋" if slide.get("includes_table") else "  "
        eq = "📐" if slide.get("includes_equation") else "  "
        print(f"  Slide {slide['slide_page']:2d} {fig}{tbl}{eq} {slide['title']}")
    print("-" * 60)

    refined_path = os.path.join(output_dir, "plan", "presentation_plan_v1.json")
    assert os.path.exists(refined_path), f"修改后大纲文件未生成: {refined_path}"
    logger.info(f"✅ 输出文件: {refined_path}")

    # ── 总结 ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉 所有测试通过!")
    print(f"   输出目录: {output_dir}")
    print(f"   v0 大纲: {len(presentation_plan)} 页")
    print(f"   v1 大纲: {len(refined_plan)} 页")
    print("=" * 60)


if __name__ == "__main__":
    main()
