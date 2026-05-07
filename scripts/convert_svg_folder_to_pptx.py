#!/usr/bin/env python3
"""
将 assets/svg/ 目录下的所有 SVG 文件按文件名排序，
先内联 CSS class 样式、再走完整 SVG 后处理管线（finalize_single_svg），
最后调用项目中已有的 create_pptx_with_native_svg 合并为单个可编辑 PPTX。

改进点：
1. 自动检测 SVG viewBox 尺寸作为 PPTX 幻灯片尺寸（解决尺寸不匹配）
2. 仅生成 native 可编辑形状版本
3. 支持 --style-protocol 注入母版背景
4. 支持 --notes-dir 读取演讲者备注

Usage:
    python scripts/convert_svg_folder_to_pptx.py
    python scripts/convert_svg_folder_to_pptx.py --svg-dir assets/svg --output assets/svg/merged_output.pptx
    python scripts/convert_svg_folder_to_pptx.py --style-protocol docs/style.md
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

# 将项目根目录加入 sys.path，以便导入 pipeline 模块
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.svg_to_pptx import create_pptx_with_native_svg
from pipeline.svg_to_pptx.master_chrome import extract_master_chrome_svg
from pipeline.svg_to_pptx.pptx_dimensions import get_viewbox_dimensions
from pipeline.svg_to_pptx.pptx_discovery import find_notes_files
from pipeline.svg_validator import finalize_single_svg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SVG_NS = "http://www.w3.org/2000/svg"


# =============================================================================
# CSS class 内联
# =============================================================================

def _parse_css_rules(style_text: str) -> dict[str, dict[str, str]]:
    """从 <style> 文本中提取类选择器规则。"""
    rules: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"\.\s*([A-Za-z0-9_\-]+)\s*\{([^}]*)\}")
    for match in pattern.finditer(style_text):
        class_name = match.group(1)
        body = match.group(2)
        props: dict[str, str] = {}
        for decl in body.split(";"):
            decl = decl.strip()
            if not decl or ":" not in decl:
                continue
            prop, val = decl.split(":", 1)
            prop = prop.strip()
            val = val.strip()
            if prop and val:
                props[prop] = val
        if props:
            rules[class_name] = props
    return rules


def inline_svg_css_classes(svg_path: str) -> None:
    """将 SVG 中 <style> 定义的 CSS class 样式内联到对应元素的属性上。"""
    tree = ET.parse(svg_path)
    root = tree.getroot()

    all_rules: dict[str, dict[str, str]] = {}
    for style_elem in root.iter():
        tag = style_elem.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        if tag == "style":
            style_text = "".join(style_elem.itertext())
            rules = _parse_css_rules(style_text)
            all_rules.update(rules)

    if not all_rules:
        return

    _UNIT_RE = re.compile(r"^([-\d.]+)\s*px$")

    for elem in root.iter():
        class_attr = elem.get("class")
        if not class_attr:
            continue

        class_names = [c.strip() for c in class_attr.split() if c.strip()]
        merged_props: dict[str, str] = {}
        for cn in class_names:
            if cn in all_rules:
                merged_props.update(all_rules[cn])

        if not merged_props:
            continue

        existing_inline: dict[str, str] = {}
        style_str = elem.get("style", "")
        if style_str:
            for decl in style_str.split(";"):
                decl = decl.strip()
                if not decl or ":" not in decl:
                    continue
                prop, val = decl.split(":", 1)
                existing_inline[prop.strip()] = val.strip()

        final_props = dict(merged_props)
        final_props.update(existing_inline)
        for attr in list(final_props.keys()):
            if elem.get(attr) is not None:
                final_props[attr] = elem.get(attr)

        for prop, val in final_props.items():
            if prop == "style":
                continue
            m = _UNIT_RE.match(val)
            if m:
                val = m.group(1)
            if elem.get(prop) is None:
                elem.set(prop, val)

        if "class" in elem.attrib:
            del elem.attrib["class"]

    for style_elem in list(root.iter()):
        tag = style_elem.tag
        if "}" in tag:
            tag = tag.split("}", 1)[1]
        if tag == "style":
            parent = None
            for p in root.iter():
                for child in list(p):
                    if child is style_elem:
                        parent = p
                        break
                if parent is not None:
                    break
            if parent is not None:
                parent.remove(style_elem)

    tree.write(svg_path, encoding="utf-8", xml_declaration=True)


# =============================================================================
# 主流程
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="将目录下的 SVG 文件经过完整后处理后合并为可编辑 PPTX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # 默认：处理 assets/svg/
  %(prog)s --svg-dir assets/svg --output out.pptx
  %(prog)s --style-protocol docs/style.md     # 注入母版背景
  %(prog)s --notes-dir assets/svg/notes       # 嵌入演讲者备注
        """,
    )
    parser.add_argument(
        "--svg-dir",
        type=str,
        default=str(PROJECT_ROOT / "assets" / "svg"),
        help="包含 SVG 文件的目录 (默认: assets/svg)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出 PPTX 路径 (默认: {svg_dir}/merged_output.pptx)",
    )
    parser.add_argument(
        "--style-protocol",
        type=str,
        default=None,
        help="style protocol markdown 文件路径，用于提取 Master Chrome 注入母版",
    )
    parser.add_argument(
        "--notes-dir",
        type=str,
        default=None,
        help="notes 目录路径（默认: {svg_dir}/notes）",
    )
    parser.add_argument(
        "--no-css-inline",
        action="store_true",
        help="跳过 CSS class 内联",
    )
    parser.add_argument(
        "--no-finalize",
        action="store_true",
        help="跳过 finalize_single_svg 后处理",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="保留临时后处理目录（调试用）",
    )
    args = parser.parse_args()

    svg_dir = Path(args.svg_dir).resolve()
    if not svg_dir.exists():
        logger.error(f"SVG 目录不存在: {svg_dir}")
        sys.exit(1)

    # 收集并排序所有 svg 文件
    svg_files_raw = sorted(svg_dir.glob("*.svg"), key=lambda p: p.name)
    if not svg_files_raw:
        logger.error(f"目录下未找到 SVG 文件: {svg_dir}")
        sys.exit(1)

    logger.info(f"发现 {len(svg_files_raw)} 个 SVG 文件，按文件名排序:")
    for p in svg_files_raw:
        logger.info(f"  - {p.name}")

    # 自动检测画布尺寸（从第一个 SVG 的 viewBox）
    custom_pixels = get_viewbox_dimensions(svg_files_raw[0])
    if custom_pixels:
        logger.info(f"自动检测幻灯片尺寸: {custom_pixels[0]} x {custom_pixels[1]} px (来自 viewBox)")
    else:
        logger.info("未检测到 viewBox，使用默认尺寸")

    # 检查所有 SVG 尺寸是否一致
    for p in svg_files_raw[1:]:
        px = get_viewbox_dimensions(p)
        if px and px != custom_pixels:
            logger.warning(f"  尺寸不一致: {p.name} 为 {px[0]}x{px[1]}，与首个文件 {custom_pixels[0]}x{custom_pixels[1]} 不同")

    # 输出路径
    output_path = args.output
    if output_path is None:
        output_path = str(svg_dir / "merged_output.pptx")
    output_path = Path(output_path).resolve()

    # style protocol / master chrome
    master_chrome_svg_text: str | None = None
    if args.style_protocol:
        sp_path = Path(args.style_protocol)
        if sp_path.exists():
            master_chrome_svg_text = extract_master_chrome_svg(sp_path.read_text(encoding="utf-8"))
            if master_chrome_svg_text:
                logger.info("Master Chrome SVG 已从 style protocol 提取")
            else:
                logger.info("style protocol 中未找到 Master Chrome Contract")
        else:
            logger.warning(f"style protocol 文件不存在: {sp_path}")

    # notes
    notes_dir = args.notes_dir
    if notes_dir is None:
        notes_dir_candidate = svg_dir / "notes"
        if notes_dir_candidate.exists():
            notes_dir = str(notes_dir_candidate)

    notes: dict[str, str] = {}
    if notes_dir:
        notes = find_notes_files(Path(notes_dir), svg_files_raw)
        if notes:
            logger.info(f"发现 {len(notes)} 个 notes 文件")

    # 创建临时目录，复制 SVG 并执行后处理
    if args.keep_temp:
        temp_dir = Path(tempfile.mkdtemp(prefix="svg_finalize_"))
        logger.info(f"临时后处理目录: {temp_dir} (keep-temp=True，不会自动删除)")
    else:
        temp_ctx = tempfile.TemporaryDirectory(prefix="svg_finalize_")
        temp_dir = Path(temp_ctx.name)
        logger.info(f"临时后处理目录: {temp_dir}")

    processed_paths: list[Path] = []
    try:
        for src in svg_files_raw:
            dst = temp_dir / src.name
            shutil.copyfile(str(src), str(dst))
            os.chmod(str(dst), stat.S_IWRITE | stat.S_IREAD)

            if not args.no_css_inline:
                logger.info(f"CSS 内联: {src.name}")
                inline_svg_css_classes(str(dst))

            if not args.no_finalize:
                logger.info(f"finalize: {src.name}")
                success, error = finalize_single_svg(str(dst))
                if not success:
                    logger.error(f"  -> finalize 失败: {error}")
                    sys.exit(1)

            processed_paths.append(dst)

        logger.info(f"生成 PPTX: {output_path}")
        ok = create_pptx_with_native_svg(
            svg_files=processed_paths,
            output_path=output_path,
            canvas_format=None,
            verbose=True,
            use_native_shapes=True,
            use_compat_mode=False,
            master_chrome_svg_text=master_chrome_svg_text,
            notes=notes,
            enable_notes=bool(notes),
        )

    finally:
        if not args.keep_temp:
            temp_ctx.cleanup()

    if ok:
        logger.info("✅ 成功生成 PPTX")
    else:
        logger.error("❌ PPTX 生成失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
