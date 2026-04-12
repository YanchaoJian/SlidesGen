"""从 slide_reports 计算幻灯片质量统计指标。"""

from typing import Any, Dict, List, Optional


def compute_slide_metrics(
    slide_reports: Dict[int, Dict[str, Any]],
    presentation_plan: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    根据 slide_reports 计算质量指标。

    Args:
        slide_reports: {slide_page: SlideReport} 字典。
        presentation_plan: 计划列表（用于计算缺页）。

    Returns:
        slide_metrics 字典，可直接合并进 run_stats.json。
    """
    if not slide_reports:
        return {}

    planned = len(presentation_plan) if presentation_plan else 0
    produced_pages = sorted(slide_reports.keys())
    total = len(produced_pages)

    # 缺页检测
    if presentation_plan:
        expected = {int(s.get("slide_page")) for s in presentation_plan if s.get("slide_page") is not None}
        missing = sorted(expected - set(produced_pages))
    else:
        missing = []

    # 逐页统计
    svg_first_pass = 0
    design_first_pass = 0
    selfheal_attempted = 0
    selfheal_succeeded = 0
    svg_retries_sum = 0
    design_retries_sum = 0
    per_slide: Dict[str, Dict[str, Any]] = {}

    for page, report in slide_reports.items():
        svg_r = report.get("svg_review") or {}
        design_r = report.get("design_review") or {}

        svg_retry = svg_r.get("retry_count", 0)
        design_retry = design_r.get("retry_count", 0)
        svg_ok = svg_r.get("verified", False)
        design_ok = design_r.get("verified", False)

        # 首次通过：retry_count == 0 且最终 verified
        if svg_retry == 0 and svg_ok:
            svg_first_pass += 1
        if design_retry == 0 and design_ok:
            design_first_pass += 1

        # 自愈：有重试的页面中最终成功的比例
        had_retry = svg_retry > 0 or design_retry > 0
        if had_retry:
            selfheal_attempted += 1
            if svg_ok and design_ok:
                selfheal_succeeded += 1

        svg_retries_sum += svg_retry
        design_retries_sum += design_retry

        per_slide[str(page)] = {
            "svg_retries": svg_retry,
            "design_retries": design_retry,
            "svg_verified": svg_ok,
            "design_verified": design_ok,
        }

    return {
        "planned_slides": planned,
        "produced_slides": total,
        "missing_pages": missing,
        "svg_first_pass_rate": round(svg_first_pass / total, 3) if total else 0,
        "design_first_pass_rate": round(design_first_pass / total, 3) if total else 0,
        "selfheal_success_rate": round(selfheal_succeeded / selfheal_attempted, 3) if selfheal_attempted else None,
        "avg_svg_retries": round(svg_retries_sum / total, 2) if total else 0,
        "avg_design_retries": round(design_retries_sum / total, 2) if total else 0,
        "slide_completion_rate": round(total / planned, 3) if planned else None,
        "per_slide": per_slide,
    }
