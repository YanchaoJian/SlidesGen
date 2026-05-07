"""
评估结果可视化。

将 eval_result.json / slide_metrics.json / comparison_summary.json
转换为 SVG 图表，输出到对应的 graphs/ 目录。

用法:
    # 单次运行的可视化
    python metrics/plot.py --session 0415_2157_GCM

    # 对比实验可视化
    python metrics/plot.py --comparison

依赖:
    pip install matplotlib numpy
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ── 颜色与标签配置 ───────────────────────────────────────────────────────────

METHOD_COLORS = {
    "SlidesGen":   "#7c3aed",
    "PPTAgent":    "#2563eb",
    "AutoPresent": "#059669",
    "AutoSlides":  "#ea580c",
    "DeepPresenter": "#db2777",
}
DEFAULT_COLOR = "#64748b"

DIMS = ["content", "design", "style_transfer"]
DIMS_ZH = ["内容质量", "视觉设计", "风格迁移"]

# 尝试设置中文字体（Windows 常见字体）
if HAS_MPL:
    import matplotlib.font_manager as fm
    _candidates = ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"]
    _font_found = False
    for _font_name in _candidates:
        try:
            plt.rcParams["font.family"] = [_font_name, "sans-serif"]
            _font_found = True
            break
        except Exception:
            continue
    if not _font_found:
        plt.rcParams["font.family"] = ["sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False


# ── 单次运行可视化 ───────────────────────────────────────────────────────────

def _load_eval_result(eval_file: Path) -> dict:
    """加载 eval_result.json，处理多模型 key 格式，返回最新一次评估结果。"""
    with open(eval_file, encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict):
        # 如果是旧格式直接包含 content/design/style_transfer
        if "content" in raw and isinstance(raw["content"], dict) and "score" in raw["content"]:
            return raw
        # 新格式: {model_name: [eval_item, ...]}
        if raw:
            model_key = list(raw.keys())[-1]
            items = raw[model_key]
            if isinstance(items, list) and items:
                return items[-1]
    return {}


def plot_radar_single(eval_result: dict, output_path: str, title: str = "评估得分雷达图"):
    """单次运行的三维雷达图。"""
    if not HAS_MPL:
        return

    scores = [
        eval_result.get("content", {}).get("score", 0),
        eval_result.get("design", {}).get("score", 0),
        (eval_result.get("style_transfer") or {}).get("score", 0),
    ]

    angles = np.linspace(0, 2 * np.pi, len(DIMS_ZH), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, scores_plot, "o-", linewidth=2, color="#7c3aed")
    ax.fill(angles, scores_plot, alpha=0.25, color="#7c3aed")
    ax.set_thetagrids(np.degrees(angles[:-1]), DIMS_ZH, fontsize=12)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
    ax.grid(True, alpha=0.3)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  [OK] {output_path}")


def plot_bar_single(eval_result: dict, slide_metrics: dict, output_path: str):
    """单次运行：评估分数 + 生成质量双柱状图。"""
    if not HAS_MPL:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 左：三维评分
    scores = [
        eval_result.get("content", {}).get("score", 0),
        eval_result.get("design", {}).get("score", 0),
        (eval_result.get("style_transfer") or {}).get("score", 0),
    ]
    bars = ax1.bar(DIMS_ZH, scores, color=["#7c3aed", "#2563eb", "#db2777"], alpha=0.8)
    ax1.set_ylim(0, 5)
    ax1.set_title("LLM-as-Judge 三维评分", fontsize=12, fontweight="bold")
    ax1.set_ylabel("分数 (0-5)")
    for bar, score in zip(bars, scores):
        ax1.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            f"{score:.1f}", ha="center", va="bottom", fontweight="bold"
        )

    # 右：生成质量指标
    if slide_metrics:
        metrics_map = {
            "SVG\n首通率": slide_metrics.get("svg_first_pass_rate", 0),
            "设计\n首通率": slide_metrics.get("design_first_pass_rate", 0),
            "自愈成功率": slide_metrics.get("selfheal_success_rate") or 0,
            "幻灯片\n完成率": slide_metrics.get("slide_completion_rate") or 0,
        }
        bars2 = ax2.bar(
            list(metrics_map.keys()),
            [v * 100 for v in metrics_map.values()],
            color="#059669", alpha=0.8
        )
        ax2.set_ylim(0, 100)
        ax2.set_title("生成过程质量指标", fontsize=12, fontweight="bold")
        ax2.set_ylabel("百分比 (%)")
        for bar, val in zip(bars2, metrics_map.values()):
            ax2.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val * 100:.1f}%", ha="center", va="bottom", fontsize=9
            )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  [OK] {output_path}")


# ── 对比实验可视化 ───────────────────────────────────────────────────────────

def plot_radar_comparison(summary: dict, output_path: str):
    """对比实验：多方法雷达图（跨论文平均值）。"""
    if not HAS_MPL:
        return

    # 按方法聚合（跨所有论文取均值）
    method_avgs: dict[str, list[list[float]]] = {}
    for paper, methods in summary.items():
        for method, scores in methods.items():
            if method not in method_avgs:
                method_avgs[method] = []
            method_avgs[method].append([
                scores.get("content", 0) or 0,
                scores.get("design", 0) or 0,
                scores.get("style_transfer", 0) or 0,
            ])

    method_mean = {
        m: [sum(s[i] for s in v) / len(v) for i in range(3)]
        for m, v in method_avgs.items()
    }

    angles = np.linspace(0, 2 * np.pi, 3, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for method, means in method_mean.items():
        color = METHOD_COLORS.get(method, DEFAULT_COLOR)
        values = means + means[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=method, color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), DIMS_ZH, fontsize=13)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title("方法对比雷达图（各论文平均）", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=11)
    ax.grid(True, alpha=0.3)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  [OK] {output_path}")


def plot_bar_comparison(summary: dict, output_path: str):
    """对比实验：分维度分组柱状图。"""
    if not HAS_MPL:
        return

    method_avgs: dict[str, dict[str, list[float]]] = {}
    for paper, methods in summary.items():
        for method, scores in methods.items():
            if method not in method_avgs:
                method_avgs[method] = {"content": [], "design": [], "style_transfer": []}
            for dim in ["content", "design", "style_transfer"]:
                v = scores.get(dim) or 0
                method_avgs[method][dim].append(v)

    methods = list(method_avgs.keys())
    dim_keys = ["content", "design", "style_transfer"]

    x = np.arange(len(DIMS_ZH))
    width = 0.8 / len(methods) if methods else 0.2
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, method in enumerate(methods):
        avgs = [
            sum(method_avgs[method][d]) / max(1, len(method_avgs[method][d]))
            for d in dim_keys
        ]
        color = METHOD_COLORS.get(method, DEFAULT_COLOR)
        offset = (i - len(methods) / 2 + 0.5) * width
        bars = ax.bar(x + offset, avgs, width * 0.9, label=method, color=color, alpha=0.85)
        for bar, v in zip(bars, avgs):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f"{v:.2f}", ha="center", va="bottom", fontsize=8
            )

    ax.set_ylabel("得分 (0-5)", fontsize=12)
    ax.set_title("各维度方法对比（均值）", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(DIMS_ZH, fontsize=12)
    ax.set_ylim(0, 5.5)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  [OK] {output_path}")


def plot_heatmap_comparison(summary: dict, dim: str, output_path: str, dim_zh: str = ""):
    """对比实验：某维度的论文×方法热力图。"""
    if not HAS_MPL:
        return

    papers = sorted(summary.keys())
    methods = sorted({m for p in summary.values() for m in p.keys()})

    data = np.zeros((len(methods), len(papers)))
    for j, paper in enumerate(papers):
        for i, method in enumerate(methods):
            data[i, j] = (summary.get(paper, {}).get(method, {}) or {}).get(dim, 0) or 0

    fig_w = max(6, len(papers) * 1.5)
    fig_h = max(4, len(methods) * 0.8)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(data, cmap="YlOrRd", vmin=0, vmax=5, aspect="auto")
    plt.colorbar(im, ax=ax, label="得分 (0-5)")

    ax.set_xticks(range(len(papers)))
    ax.set_yticks(range(len(methods)))
    ax.set_xticklabels(papers, rotation=30, ha="right", fontsize=10)
    ax.set_yticklabels(methods, fontsize=11)
    ax.set_title(f"{dim_zh or dim} — 论文×方法热力图", fontsize=13, fontweight="bold")

    for i in range(len(methods)):
        for j in range(len(papers)):
            ax.text(
                j, i, f"{data[i, j]:.1f}", ha="center", va="center",
                fontsize=9, color="black" if data[i, j] < 3.5 else "white"
            )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  [OK] {output_path}")


# ── CLI 入口 ─────────────────────────────────────────────────────────────────

def cmd_session(session_id: str):
    """生成单次运行的可视化图表。"""
    eval_dir = ROOT / "eval" / "runs" / session_id
    graphs_dir = eval_dir / "graphs"

    eval_file = eval_dir / "eval_result.json"
    metrics_file = eval_dir / "slide_metrics.json"

    if not eval_file.exists():
        print(f"[ERROR] 找不到 {eval_file}")
        return

    eval_result = _load_eval_result(eval_file)
    if not eval_result:
        print(f"[ERROR] 无法解析 {eval_file}")
        return

    slide_metrics = {}
    if metrics_file.exists():
        with open(metrics_file, encoding="utf-8") as f:
            slide_metrics = json.load(f)

    print(f"生成 session {session_id} 的可视化图表...")
    plot_radar_single(eval_result, str(graphs_dir / "评估分数雷达图.svg"))
    plot_bar_single(eval_result, slide_metrics, str(graphs_dir / "综合评估柱状图.svg"))


def cmd_comparison():
    """生成对比实验的可视化图表。"""
    summary_file = ROOT / "eval" / "comparison" / "comparison_summary.json"
    graphs_dir = ROOT / "eval" / "comparison" / "graphs"

    if not summary_file.exists():
        print(f"[ERROR] 找不到 {summary_file}，请先运行对比评估脚本生成汇总数据")
        return

    with open(summary_file, encoding="utf-8") as f:
        summary = json.load(f)

    print("生成对比实验可视化图表...")
    plot_radar_comparison(summary, str(graphs_dir / "方法对比雷达图.svg"))
    plot_bar_comparison(summary, str(graphs_dir / "维度对比柱状图.svg"))
    for dim, dim_zh in zip(["content", "design", "style_transfer"], DIMS_ZH):
        plot_heatmap_comparison(
            summary, dim,
            str(graphs_dir / f"{dim_zh}热力图.svg"),
            dim_zh=dim_zh,
        )


def main():
    if not HAS_MPL:
        print("[ERROR] matplotlib / numpy 未安装，无法生成图表。请执行: pip install matplotlib numpy")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="SlidesGen 评估结果可视化")
    parser.add_argument("--session", help="单次运行 session_id（如 0415_2157_GCM）")
    parser.add_argument("--comparison", action="store_true", help="生成对比实验图表")
    args = parser.parse_args()

    if args.session:
        cmd_session(args.session)
    elif args.comparison:
        cmd_comparison()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
