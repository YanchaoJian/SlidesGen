"""
SVG → PPTX 转换模块。

将 SVG 源码转换为包含可编辑 DrawingML 原生形状的 PPTX 文件。

核心 API:
    convert_svg_to_slide_shapes(svg_path)
        解析单个 SVG 文件，返回 (slide_xml, media_files, rel_entries)。

    create_pptx_with_native_svg(svg_files, output_path, ...)
        将多个 SVG 文件合并为一个 PPTX 演示文稿。
"""

from agents.composer.svg_converter.svg_to_pptx import (
    convert_svg_to_slide_shapes,
    create_pptx_with_native_svg,
)

__all__ = [
    "convert_svg_to_slide_shapes",
    "create_pptx_with_native_svg",
]
