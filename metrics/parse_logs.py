#!/usr/bin/env python
"""
从 run_stats.json 提取实验数据并打印 Markdown 报告。

用法:
    python metrics/parse_logs.py --session_id 0408_1155_MS
    python metrics/parse_logs.py --session_id 0408_1155_MS --output_dir output
"""

import argparse
import json
import os
import sys


def _fmt_pct(val):
    """格式化百分比，None 显示为 N/A。"""
    if val is None:
        return "N/A"
    return f"{val * 100:.1f}%"


def _fmt_num(val):
    if val is None:
        return "N/A"
    return f"{val}"


def print_report(stats: dict):
    """打印结构化 Markdown 报告。"""
    print(f"# Session: {stats.get('session_id', 'unknown')}\n")

    # ── 基础信息 ──
    print("## Overview\n")
    print(f"| Item | Value |")
    print(f"|------|-------|")
    print(f"| Status | {stats.get('status', 'unknown')} |")
    print(f"| End-to-end (sec) | {stats.get('end_to_end_sec', 'N/A')} |")
    print(f"| Wall start | {stats.get('wall_start', '')} |")
    print(f"| Wall end | {stats.get('wall_end', '')} |")
    print(f"| Resumed | {stats.get('is_resumed', False)} |")

    models = stats.get("models", {})
    if models:
        print(f"| Model (default) | {models.get('model_name', '')} |")
        print(f"| Vision model | {models.get('vision_model', '')} |")
        print(f"| SVG model | {models.get('svg_model', '')} |")
        print(f"| Text model | {models.get('text_model', '')} |")

    error = stats.get("error")
    if error:
        print(f"| Error | {error} |")
    print()

    # ── Slide 质量指标 ──
    sm = stats.get("slide_metrics") or {}
    if sm:
        print("## Slide Quality Metrics\n")
        print(f"| Metric | Value |")
        print(f"|--------|-------|")
        print(f"| Planned slides | {sm.get('planned_slides', 'N/A')} |")
        print(f"| Produced slides | {sm.get('produced_slides', 'N/A')} |")
        print(f"| Slide completion rate | {_fmt_pct(sm.get('slide_completion_rate'))} |")
        print(f"| SVG first-pass rate | {_fmt_pct(sm.get('svg_first_pass_rate'))} |")
        print(f"| Design first-pass rate | {_fmt_pct(sm.get('design_first_pass_rate'))} |")
        print(f"| Self-heal success rate | {_fmt_pct(sm.get('selfheal_success_rate'))} |")
        print(f"| Avg SVG retries | {_fmt_num(sm.get('avg_svg_retries'))} |")
        print(f"| Avg design retries | {_fmt_num(sm.get('avg_design_retries'))} |")

        missing = sm.get("missing_pages", [])
        if missing:
            print(f"| Missing pages | {missing} |")
        print()

        # 逐页明细
        per_slide = sm.get("per_slide", {})
        if per_slide:
            print("### Per-Slide Detail\n")
            print("| Page | SVG retries | SVG ok | Design retries | Design ok |")
            print("|------|-------------|--------|----------------|-----------|")
            for page in sorted(per_slide.keys(), key=lambda x: int(x)):
                s = per_slide[page]
                svg_ok = "Y" if s.get("svg_verified") else "N"
                des_ok = "Y" if s.get("design_verified") else "N"
                print(f"| {page} | {s.get('svg_retries', 0)} | {svg_ok} | {s.get('design_retries', 0)} | {des_ok} |")
            print()
    else:
        print("## Slide Quality Metrics\n")
        print("_No slide_reports data (session predates slide_reports feature)._\n")

    # ── Token 消耗 ──
    tokens_total = stats.get("tokens_total", {})
    if tokens_total:
        print("## Token Usage\n")
        print(f"| Metric | Value |")
        print(f"|--------|-------|")
        print(f"| Total prompt tokens | {tokens_total.get('prompt_tokens', 0)} |")
        print(f"| Total completion tokens | {tokens_total.get('completion_tokens', 0)} |")
        print(f"| Total cost (USD) | ${tokens_total.get('cost_usd', 0):.4f} |")
        print()

        by_model = stats.get("tokens_by_model", {})
        if by_model:
            print("### By Model\n")
            print("| Model | Prompt | Completion | Cost (USD) |")
            print("|-------|--------|------------|------------|")
            for model, info in sorted(by_model.items()):
                print(f"| {model} | {info.get('prompt_tokens',0)} | {info.get('completion_tokens',0)} | ${info.get('cost_usd',0):.4f} |")
            print()

    # ── 节点耗时 ──
    node_stats = stats.get("per_node_sec", {})
    if node_stats:
        print("## Node Timing\n")
        print("| Node | Total (s) | Count | Avg (s) |")
        print("|------|-----------|-------|---------|")
        for name in sorted(node_stats.keys()):
            n = node_stats[name]
            print(f"| {name} | {n.get('total', 0):.2f} | {n.get('count', 0)} | {n.get('avg', 0):.2f} |")
        print()

    # ── 警告 ──
    warnings = stats.get("warnings", [])
    if warnings:
        print("## Warnings\n")
        for w in warnings:
            print(f"- {w}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Parse SlidesGen run_stats.json and print report.")
    parser.add_argument("--session_id", required=True, help="Session ID (output subdirectory name)")
    parser.add_argument("--output_dir", default="output", help="Output root directory (default: output)")
    parser.add_argument("--out_file", help="Optional path to save the Markdown report to a new file")
    args = parser.parse_args()

    stats_path = os.path.join(args.output_dir, args.session_id, "run_stats.json")
    if not os.path.exists(stats_path):
        print(f"Error: {stats_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    if args.out_file:
        with open(args.out_file, "w", encoding="utf-8") as f:
            old_stdout = sys.stdout
            sys.stdout = f
            try:
                print_report(stats)
            finally:
                sys.stdout = old_stdout
    else:
        print_report(stats)


if __name__ == "__main__":
    main()
