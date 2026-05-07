"""
对比实验批量评估脚本。

从 eval/baselines/ 读取各方法生成的 PPTX，
用 SlidesGen 的 LLM-as-Judge 框架统一评估，
结果写入对应目录，并汇总到 eval/comparison/comparison_summary.json。

基线方法不对齐 style_image_path（各方法输入不同），
因此 D3 风格迁移维度对基线评估会跳过。

用法:
    # 评估所有基线
    python metrics/run_eval_comparison.py

    # 仅评估某个方法
    python metrics/run_eval_comparison.py --method PPTAgent

    # 仅评估某个论文
    python metrics/run_eval_comparison.py --paper paper_01

    # 把 SlidesGen 某次运行结果也加入对比汇总（默认用 session_id 作为论文 key）
    python metrics/run_eval_comparison.py --add-run 0415_2157_GCM

    # 把 SlidesGen 结果加入对比汇总，并指定论文名
    python metrics/run_eval_comparison.py --add-run 0415_2157_GCM --paper Transformer
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv()

from metrics.evaluate import evaluate_pptx
from utils.llm import LLMConfig

EVAL_BASELINES_DIR = ROOT / "eval" / "baselines"
COMPARISON_DIR = ROOT / "eval" / "comparison"
RUNS_DIR = ROOT / "eval" / "runs"


def get_llm_config() -> LLMConfig:
    return LLMConfig(
        model_name=os.getenv("EVAL_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", ""),
    )


async def eval_one(method: str, paper: str, pptx_path: Path, llm_config: LLMConfig) -> dict | None:
    """评估单个 (method, paper) 组合。"""
    # 显式指定 output_dir 为 PPTX 所在目录，使评估产物与源文件同目录
    output_dir = str(pptx_path.parent)
    print(f"  评估 [{method}] / [{paper}]  →  {output_dir}")

    try:
        result = await evaluate_pptx(
            pptx_path=str(pptx_path),
            llm_config=llm_config,
            style_image_path=None,   # 基线不对齐 style
            output_dir=output_dir,
            dpi=150,
        )
        return result
    except Exception as e:
        print(f"  [ERROR] {method}/{paper}: {e}")
        return None


def _collect_baseline_tasks(method_filter: str | None, paper_filter: str | None):
    """扫描 eval/baselines/ 下的待评估 PPTX。"""
    tasks: list[tuple[str, str, Path]] = []
    if not EVAL_BASELINES_DIR.exists():
        return tasks

    for method_dir in sorted(EVAL_BASELINES_DIR.iterdir()):
        if not method_dir.is_dir():
            continue
        if method_filter and method_dir.name != method_filter:
            continue
        for paper_dir in sorted(method_dir.iterdir()):
            if not paper_dir.is_dir():
                continue
            if paper_filter and paper_dir.name != paper_filter:
                continue
            for pptx in sorted(paper_dir.glob("*.pptx")):
                tasks.append((method_dir.name, paper_dir.name, pptx))
    return tasks


def _load_run_scores(session_id: str) -> dict | None:
    """从 eval/runs/{session}/ 读取 SlidesGen 的评估结果，转为对比汇总格式。"""
    eval_file = RUNS_DIR / session_id / "eval_result.json"
    if not eval_file.exists():
        print(f"  [WARN] 找不到 SlidesGen 评估结果: {eval_file}")
        return None

    with open(eval_file, encoding="utf-8") as f:
        raw = json.load(f)

    # 处理多模型 key 格式，取最新一次
    eval_result = {}
    if isinstance(raw, dict):
        if "content" in raw and isinstance(raw["content"], dict) and "score" in raw["content"]:
            eval_result = raw
        elif raw:
            model_key = list(raw.keys())[-1]
            items = raw[model_key]
            if isinstance(items, list) and items:
                eval_result = items[-1]

    if not eval_result:
        return None

    return {
        "content": eval_result.get("content", {}).get("score"),
        "design": eval_result.get("design", {}).get("score"),
        "style_transfer": (eval_result.get("style_transfer") or {}).get("score"),
        "color_histogram": eval_result.get("color_histogram_similarity"),
    }


def _print_table(summary: dict):
    print("\n=== 对比实验结果汇总 ===\n")
    for paper, methods in sorted(summary.items()):
        print(f"📄 {paper}")
        print(f"  {'方法':<20} {'Content':>9} {'Design':>9} {'Style':>9}")
        print(f"  {'-' * 52}")
        for method, s in sorted(methods.items()):
            c = f"{s['content']:.2f}" if s.get("content") is not None else "    N/A"
            d = f"{s['design']:.2f}" if s.get("design") is not None else "    N/A"
            st = f"{s['style_transfer']:.2f}" if s.get("style_transfer") is not None else "    N/A"
            print(f"  {method:<20} {c:>9} {d:>9} {st:>9}")
        print()


async def run_all(
    method_filter: str | None,
    paper_filter: str | None,
    add_run: str | None,
    run_paper: str | None,
):
    llm_config = get_llm_config()

    # 读取已有汇总（支持增量）
    COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = COMPARISON_DIR / "comparison_summary.json"
    summary: dict = {}
    if summary_path.exists():
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)

    # ── 1. 评估基线 ──
    tasks = _collect_baseline_tasks(method_filter, paper_filter)

    if tasks:
        print(f"共 {len(tasks)} 个基线评估任务：")
        for m, p, _ in tasks:
            print(f"  {m} / {p}")
        print()

        for method, paper, pptx_path in tasks:
            result = await eval_one(method, paper, pptx_path, llm_config)
            if result:
                if paper not in summary:
                    summary[paper] = {}
                summary[paper][method] = {
                    "content": result["content"]["score"],
                    "design": result["design"]["score"],
                    "style_transfer": (result.get("style_transfer") or {}).get("score"),
                    "color_histogram": result.get("color_histogram_similarity"),
                }
    else:
        print("没有找到待评估的基线 PPTX，请检查 eval/baselines/ 目录。")

    # ── 2. 可选：加入 SlidesGen 运行结果 ──
    if add_run:
        paper_key = run_paper or add_run
        print(f"加入 SlidesGen 结果 [{add_run}] → paper key: {paper_key}")
        run_scores = _load_run_scores(add_run)
        if run_scores:
            if paper_key not in summary:
                summary[paper_key] = {}
            summary[paper_key]["SlidesGen"] = run_scores
            print(f"  [OK] SlidesGen / {paper_key} 已加入汇总")
        else:
            print(f"  [SKIP] 无法读取 {add_run} 的评估结果")

    # ── 3. 写入汇总 ──
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n汇总结果写入：{summary_path}")
    _print_table(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="对比实验批量评估")
    parser.add_argument("--method", default=None, help="仅评估指定方法（如 PPTAgent）")
    parser.add_argument("--paper", default=None, help="仅评估指定论文目录（如 paper_01）")
    parser.add_argument("--add-run", dest="add_run", default=None,
                        help="将 SlidesGen 某次运行结果加入对比汇总（session_id）")
    parser.add_argument("--run-paper", dest="run_paper", default=None,
                        help="指定 SlidesGen 结果在汇总中的论文名（默认用 session_id）")
    args = parser.parse_args()
    asyncio.run(run_all(args.method, args.paper, args.add_run, args.run_paper))
