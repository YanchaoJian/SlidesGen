"""
测试 agents.perception.pdf_parser 模块

- 使用 Marker 模型提取 PDF
- 使用 gemini-3.1-pro-preview 修正图片方向

输入: assets/paper.pdf
输出: test/output/test_pdf_parser/ 目录
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from agents.perception.pdf_parser.extractor import extract_pdf
from agents.perception.pdf_parser.image_orientation import fix_image_orientation, _build_orientation_grid
from PIL import Image
from openai import OpenAI


def main():
    print("=" * 60)
    print("Testing agents.perception.pdf_parser module")
    print("=" * 60)
    
    # 配置路径
    pdf_path = project_root / "assets" / "paper.pdf"
    output_dir = project_root / "test" / "output" / "test_pdf_parser"
    marker_path = project_root / "models" / "marker"
    
    # 清理旧输出
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nInput PDF: {pdf_path}")
    print(f"Output directory: {output_dir}")
    print(f"Marker model path: {marker_path}")
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    # 测试 1: PDF 提取 (Marker)
    print("\n" + "-" * 40)
    print("Test 1: extract_pdf() - Marker PDF extraction")
    print("-" * 40)
    
    content, json_file, img_dir = extract_pdf(
        pdf_path=str(pdf_path),
        marker_path=str(marker_path) if marker_path.exists() else "models/marker",
        output_dir=str(output_dir),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_name="gpt-4o"  # 用于图片方向检测
    )
    
    if content is None:
        print("Failed to extract PDF content")
        return 1
    
    print(f"Extraction successful!")
    print(f"  - Text length: {len(content.get('full_text', ''))} chars")
    print(f"  - Images: {len(content.get('images', []))}")
    print(f"  - Tables: {len(content.get('tables', []))}")
    print(f"  - Equations: {len(content.get('equations', []))}")
    print(f"  - Content JSON: {json_file}")
    
    # 显示提取的图片路径
    for img_info in content.get('images', [])[:3]:
        print(f"  - Image: {img_info.get('path', 'N/A')}")
    
    # 测试 2: 图片方向修正 (gemini-3.1-pro-preview)
    print("\n" + "-" * 40)
    print("Test 2: image_orientation - Gemini direction fix")
    print("-" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        print("Skipped (no OPENAI_API_KEY)")
        return 0
    
    # 创建测试图片
    test_img = Image.new('RGB', (400, 300), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(test_img)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    draw.text((50, 130), "Hello World - Test", fill='black', font=font)
    
    # 创建测试输出目录
    orientation_dir = output_dir / "orientation_test"
    orientation_dir.mkdir(exist_ok=True)
    
    # 1. 保存原始图片
    original_path = orientation_dir / "01_original.png"
    test_img.save(original_path)
    print(f"[1] Original image: {original_path}")
    
    # 2. 构建并保存方向检测网格
    grid = _build_orientation_grid(test_img)
    grid_path = orientation_dir / "02_orientation_grid.png"
    grid.save(grid_path)
    print(f"[2] Orientation grid: {grid_path}")
    
    # 3. 创建旋转图片并保存
    rotated_img = test_img.rotate(90, expand=True)
    rotated_path = orientation_dir / "03_rotated_90.png"
    rotated_img.save(rotated_path)
    print(f"[3] Rotated 90°: {rotated_path}")
    
    # 4. 使用 Gemini 修正方向并保存
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    print(f"\nCalling Gemini API (gemini-3.1-pro-preview)...")
    result = fix_image_orientation(rotated_img, client, model="gemini-3.1-pro-preview")
    
    fixed_path = orientation_dir / "04_fixed.png"
    result.save(fixed_path)
    print(f"[4] Fixed image: {fixed_path}")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print(f"\nOutput directory: {output_dir}")
    print("\nGenerated files:")
    print(f"  - Content JSON: raw/pdf-content.json")
    print(f"  - Extracted images: images/_page_*.jpeg")
    print(f"  - Orientation test: orientation_test/")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
