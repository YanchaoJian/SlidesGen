"""手动合并指定目录下各 slide 的 SVG 文件为完整 PPTX。

用法: python -m scripts.merge_slides --result_dir output/0116_2040/result --output_dir output/0116_2040
"""
import argparse
from pathlib import Path

from utils.pptx_merger import merge_svgs_to_pptx


def merge_slides(result_dir: str, output_dir: str):
    """收集各 slide 目录下最新的 slide_v*.svg，合并为完整 PPTX。"""
    result_dir = Path(result_dir).resolve()
    output_dir = Path(output_dir).resolve()

    svg_paths = []
    for slide_dir in sorted(result_dir.glob("slide_*")):
        if not slide_dir.is_dir():
            continue
        svg_files = sorted(slide_dir.glob("slide_v*.svg"))
        if svg_files:
            svg_paths.append(str(svg_files[-1]))

    if not svg_paths:
        print(f"  No slide SVG files found at: {result_dir}")
        return

    print(f"Found {len(svg_paths)} slide SVG files:")
    for path in svg_paths:
        print(f"  - {path}")

    final_path = output_dir / "result" / "Final_Presentation.pptx"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nMerging to: {final_path}")
    result = merge_svgs_to_pptx(svg_paths, str(final_path))
    if result:
        print(f"Done! Saved to: {final_path}")
    else:
        print("Merge failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", default="output/0116_2014/result")
    parser.add_argument("--output_dir", default="output/0116_2014")
    args = parser.parse_args()

    merge_slides(args.result_dir, args.output_dir)
