"""手动合并指定目录下的 PPTX 文件。用法: python -m scripts.merge_slides --result_dir ... --output_dir ..."""
import argparse
from pathlib import Path

from agent.composer.pptx_renderer import merge_deck


def test_merge_slides(result_dir: str, output_dir: str):
    """测试合并 PPTX 文件"""
    result_dir = Path(result_dir).resolve()
    output_dir = Path(output_dir).resolve()

    slide_paths = [
        str(p) for p in result_dir.rglob("*.pptx")
        if p.name != "Final_Presentation.pptx"
    ]

    if not slide_paths:
        print(f"  No PPTX files found at: {result_dir}")
        return

    slide_paths = sorted(slide_paths)
    print(f"Found {len(slide_paths)} PPTX files:")
    for path in slide_paths:
        print(f"  - {path}")

    final_path = output_dir / "result" / "Final_Presentation.pptx"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nMerging to: {final_path}")
    merge_deck(slide_paths, str(final_path))
    print(f"Done! Saved to: {final_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", default="output/0116_2014/result")
    parser.add_argument("--output_dir", default="output/0116_2014")
    args = parser.parse_args()

    test_merge_slides(args.result_dir, args.output_dir)
