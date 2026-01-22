import os
import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
        print(f"⚠️ 未找到任何 PPTX 文件，检查路径是否存在: {result_dir}")
        return

    slide_paths = sorted(slide_paths)
    print(f"📄 找到 {len(slide_paths)} 个 PPTX 文件:")
    for path in slide_paths:
        print(f"  - {path}")

    final_path = output_dir / "result" / "Final_Presentation.pptx"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\n🔄 正在合并到: {final_path}")
    merge_deck(slide_paths, str(final_path))
    print(f"✅ 合并完成！文件已保存到: {final_path}")


if __name__ == "__main__":
    # 可传入自定义目录，否则默认
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", default="output/0116_2014/result")
    parser.add_argument("--output_dir", default="output/0116_2014")
    args = parser.parse_args()

    test_merge_slides(args.result_dir, args.output_dir)