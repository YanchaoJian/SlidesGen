"""
测试程序：检查 SVG 文本行间距问题

运行方式:
    cd S:/project/SlidesGen
    python test/test_text_spacing.py

功能:
1. 使用正则提取 SVG 中所有 <text> 元素的 y 坐标和字体大小
2. 检查相邻文本行的间距是否足够（>= 1.4em）
3. 输出检测结果
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def extract_text_elements(svg_code: str) -> List[Dict]:
    """
    使用正则从 SVG 代码中提取所有文本元素的信息。
    
    返回列表，每个元素包含:
    - y: y 坐标
    - font_size: 字体大小
    - content: 文本内容（用于调试）
    - raw: 原始匹配文本
    """
    texts = []
    
    # 匹配 <text ...>内容</text>
    # 支持多行，支持各种属性顺序
    text_pattern = r'<text\b([^>]*)>(.*?)</text>'
    
    for match in re.finditer(text_pattern, svg_code, re.DOTALL | re.IGNORECASE):
        attrs_str = match.group(1)
        content = match.group(2).strip()
        
        # 提取 y 坐标
        y_match = re.search(r'y\s*=\s*["\']?([\d.]+)', attrs_str, re.IGNORECASE)
        y = float(y_match.group(1)) if y_match else 0.0
        
        # 提取 font-size（支持 px 单位或无单位）
        fs_match = re.search(r'font-size\s*=\s*["\']?([\d.]+)', attrs_str, re.IGNORECASE)
        font_size = float(fs_match.group(1)) if fs_match else 16.0  # 默认 16px
        
        # 清理内容（移除嵌套标签，只保留文本）
        clean_content = re.sub(r'<[^>]+>', '', content)
        clean_content = ' '.join(clean_content.split())  # 合并多余空白
        
        if clean_content:  # 只记录非空文本
            texts.append({
                'y': y,
                'font_size': font_size,
                'content': clean_content[:50],  # 截取前50字符用于显示
                'raw_attrs': attrs_str[:100]
            })
    
    return texts


def check_text_spacing(texts: List[Dict], min_factor: float = 1.4) -> List[Dict]:
    """
    检查文本行间距是否足够。
    
    参数:
        texts: 文本元素列表
        min_factor: 最小行高倍数（默认 1.4em）
    
    返回:
        违规列表，每个元素包含违规详情
    """
    if len(texts) < 2:
        return []
    
    # 按 y 坐标排序
    sorted_texts = sorted(texts, key=lambda t: t['y'])
    
    violations = []
    
    for i in range(len(sorted_texts) - 1):
        current = sorted_texts[i]
        next_text = sorted_texts[i + 1]
        
        # 计算实际间距
        actual_gap = next_text['y'] - current['y']
        
        # 计算最小要求间距
        min_gap = current['font_size'] * min_factor
        
        # 如果间距不足，记录违规
        if actual_gap < min_gap:
            violations.append({
                'index': i + 1,
                'line1_y': current['y'],
                'line2_y': next_text['y'],
                'actual_gap': actual_gap,
                'min_gap': min_gap,
                'font_size': current['font_size'],
                'is_overlap': actual_gap < current['font_size'] * 0.8,  # 严重重叠判断
                'content1': current['content'],
                'content2': next_text['content']
            })
    
    return violations


def print_results(texts: List[Dict], violations: List[Dict], svg_path: str):
    """打印检查结果。"""
    print("=" * 70)
    print("SVG 文件: {}".format(svg_path))
    print("=" * 70)
    
    # 打印所有提取的文本
    print("\n找到 {} 个文本元素:\n".format(len(texts)))
    for i, t in enumerate(texts, 1):
        print("  [{}] y={:.1f}, font={:.0f}px: \"{}...\"".format(
            i, t['y'], t['font_size'], t['content'][:40]))
    
    # 打印检查结果
    print("\n" + "=" * 70)
    print("行间距检查结果")
    print("=" * 70)
    
    if not violations:
        print("\n所有文本行间距正常（>= 1.4em）")
        return
    
    print("\n发现 {} 处行间距不足:\n".format(len(violations)))
    
    for v in violations:
        severity = "严重重叠" if v['is_overlap'] else "间距不足"
        print("  {} - 第 {} 行 与 第 {} 行:".format(
            severity, v['index'], v['index']+1))
        print("      y 坐标: {:.1f}px -> {:.1f}px".format(
            v['line1_y'], v['line2_y']))
        print("      实际间距: {:.1f}px".format(v['actual_gap']))
        print("      要求间距: {:.1f}px (字体 {:.0f}px x 1.4)".format(
            v['min_gap'], v['font_size']))
        print("      缺口: {:.1f}px".format(v['min_gap'] - v['actual_gap']))
        print('      文本1: "{}..."'.format(v['content1'][:40]))
        print('      文本2: "{}..."'.format(v['content2'][:40]))
        print()
    
    # 打印建议修复
    print("=" * 70)
    print("修复建议")
    print("=" * 70)
    print("  对于检测到的文本对，应该:")
    print("  1. 合并为单个 <text> 元素，使用 <tspan> 换行")
    print("  2. <tspan> 的 dy 属性设置为 font-size x 1.4 到 1.8")
    print()
    print("  示例修复:")
    print('  <text x="88" y="307" font-size="17">')
    print("      第一行文本")
    print('      <tspan x="88" dy="24">第二行文本</tspan>  <!-- 17x1.4=24 -->')
    print("  </text>")


def main():
    # 默认测试文件
    default_path = "output/0415_1758_gpt-5.4-mini/slides/slide_02/slide_02_v2.svg"
    
    # 支持命令行传入路径
    svg_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    # 转换为绝对路径
    svg_file = Path(svg_path)
    if not svg_file.is_absolute():
        svg_file = Path("S:/project/SlidesGen") / svg_file
    
    # 检查文件是否存在
    if not svg_file.exists():
        print("文件不存在: {}".format(svg_file))
        print("   请检查路径是否正确")
        sys.exit(1)
    
    # 读取 SVG 文件
    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_code = f.read()
    except Exception as e:
        print("读取文件失败: {}".format(e))
        sys.exit(1)
    
    # 提取文本元素
    texts = extract_text_elements(svg_code)
    
    if not texts:
        print("未找到任何文本元素")
        sys.exit(0)
    
    # 检查行间距
    violations = check_text_spacing(texts)
    
    # 打印结果
    print_results(texts, violations, str(svg_file))
    
    # 返回退出码（有违规返回 1，方便脚本调用）
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
