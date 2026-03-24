"""手动合并指定目录下各 slide 的代码文件为完整 PPTX。

用法: python -m scripts.merge_slides --result_dir output/0116_2040/result --output_dir output/0116_2040
"""
import argparse
from pathlib import Path

from agent.composer.pptx_renderer import merge_deck


def merge_slides(result_dir: str, output_dir: str):
    """收集各 slide 目录下最新的 code_v*.py，合并为完整 PPTX。"""
    result_dir = Path(result_dir).resolve()
    output_dir = Path(output_dir).resolve()

    # 收集每个 slide_XX 目录下版本号最大的 code_v*.py
    code_paths = []
    for slide_dir in sorted(result_dir.glob("slide_*")):
        if not slide_dir.is_dir():
            continue
        code_files = sorted(slide_dir.glob("code_v*.py"))
        if code_files:
            code_paths.append(str(code_files[-1]))  # 取最新版本

    if not code_paths:
        print(f"  No slide code files found at: {result_dir}")
        return

    print(f"Found {len(code_paths)} slide code files:")
    for path in code_paths:
        print(f"  - {path}")

    final_path = output_dir / "result" / "Final_Presentation.pptx"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nMerging to: {final_path}")
    merge_deck(code_paths, str(final_path))
    print(f"Done! Saved to: {final_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", default="output/0116_2014/result")
    parser.add_argument("--output_dir", default="output/0116_2014")
    args = parser.parse_args()

    merge_slides(args.result_dir, args.output_dir)
