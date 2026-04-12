"""
多页 SVG 合并为 PPTX 模块。

将多个已后处理的 SVG 文件通过 DrawingML 转换器合并为一个可编辑 PPTX 演示文稿。
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from pipeline.svg_to_pptx import create_pptx_with_native_svg
from pipeline.svg_to_pptx.master_chrome import extract_master_chrome_svg

logger = logging.getLogger(__name__)


def merge_svgs_to_pptx(
    svg_paths: List[str],
    output_pptx_path: str,
    style_protocol: Optional[str] = None,
    notes: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """
    将多个已后处理的 SVG 文件合并为一个 PPTX 演示文稿。

    Args:
        svg_paths: SVG 文件路径列表（已排序、已后处理）。
        output_pptx_path: 输出 PPTX 路径。
        style_protocol: 风格协议 markdown 文本。若包含 IV-bis Master Chrome
            Contract，会从中提取 Master Chrome SVG 注入到 PPTX 母版。
        notes: 演讲者备注字典，key 为 SVG 文件 stem（不含扩展名），
            value 为备注文本。传入后会注入到对应 slide 的备注栏。

    Returns:
        成功返回 PPTX 文件路径，失败返回 None。
    """
    if not svg_paths:
        logger.warning("   -> No SVG files provided to merge.")
        return None

    # 过滤不存在的文件
    valid_paths = []
    for p in svg_paths:
        if os.path.exists(p):
            valid_paths.append(Path(p))
        else:
            logger.warning(f"   -> Skipping non-existent SVG: {p}")

    if not valid_paths:
        logger.error("   -> No valid SVG files to convert.")
        return None

    logger.info(f"   -> Converting {len(valid_paths)} SVG(s) to PPTX...")

    os.makedirs(os.path.dirname(output_pptx_path), exist_ok=True)

    chrome_svg = extract_master_chrome_svg(style_protocol)
    if chrome_svg:
        logger.info("   -> Master chrome SVG extracted from style protocol; will inject into slide master.")
    elif style_protocol:
        logger.info("   -> No Master Chrome Contract found in style protocol; PPTX will use empty master.")

    try:
        create_pptx_with_native_svg(
            svg_files=valid_paths,
            output_path=Path(output_pptx_path),
            canvas_format="ppt169",
            verbose=False,
            use_native_shapes=True,
            master_chrome_svg_text=chrome_svg,
            notes=notes,
            enable_notes=bool(notes),
        )

        if os.path.exists(output_pptx_path):
            size = os.path.getsize(output_pptx_path)
            logger.info(f"   -> PPTX created: {output_pptx_path} ({size:,} bytes)")
            return output_pptx_path
        else:
            logger.error("   -> PPTX file was not created.")
            return None

    except Exception as e:
        logger.error(f"   -> PPTX conversion failed: {e}", exc_info=True)
        return None
