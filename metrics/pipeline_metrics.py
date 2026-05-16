"""From slide_reports calculate pipeline quality metrics."""

from typing import Any, Dict, List, Optional


def compute_pipeline_metrics(
    slide_reports: Dict[int, Dict[str, Any]],
    presentation_plan: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Calculate quality metrics from slide reports.

    Args:
        slide_reports: {slide_page: SlideReport} dictionary.
        presentation_plan: List of dictionaries with slide plan.

    Returns:
        pipeline_metrics dictionary, can be directly merged into run_stats.json.
    """
    if not slide_reports:
        return {}

    planned = len(presentation_plan) if presentation_plan else 0
    # Convert keys to int for consistent comparison
    produced_pages = sorted(int(k) for k in slide_reports.keys())
    total = len(produced_pages)

    # Missing pages detection
    if presentation_plan:
        expected = {int(s.get("slide_page")) for s in presentation_plan if s.get("slide_page") is not None}
        missing = sorted(expected - set(produced_pages))
    else:
        missing = []

    # Page statistics
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

        # First pass: retry_count == 0 and final verified
        if svg_retry == 0 and svg_ok:
            svg_first_pass += 1
        if design_retry == 0 and design_ok:
            design_first_pass += 1

        # Self-healing: success rate of pages with retries
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


if __name__ == "__main__":
    import argparse
    import json
    import os

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Calculate pipeline metrics from final_snapshot.json and save to a new JSON file")
    parser.add_argument("--snapshot_path", required=True, help="Path to the final_snapshot.json file")
    parser.add_argument("--output_path", required=True, help="Path to the target output JSON file (e.g., metrics/pipeline_metrics.json)")
    args = parser.parse_args()

    if not os.path.exists(args.snapshot_path):
        print(f"Error: Snapshot file not found at {args.snapshot_path}")
        exit(1)

    # Read the original JSON
    print(f"Reading snapshot: {args.snapshot_path}")
    with open(args.snapshot_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract needed data for statistics
    slide_reports = data.get("slide_reports", {})
    presentation_plan = data.get("presentation_plan", [])
    metrics_result = compute_pipeline_metrics(slide_reports, presentation_plan)

    # Ensure the target path directory exists
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

    # Write metrics locally to the new JSON file
    with open(args.output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_result, f, indent=2, ensure_ascii=False)
        
    print(f"Metrics successfully calculated and saved to {args.output_path}.")
