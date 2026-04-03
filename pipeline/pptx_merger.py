"""
多页 SVG 合并为 PPTX 模块。

将多个已后处理的 SVG 文件通过 DrawingML 转换器合并为一个可编辑 PPTX 演示文稿。
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

from pipeline.svg_to_pptx import create_pptx_with_native_svg

logger = logging.getLogger(__name__)


def merge_svgs_to_pptx(svg_paths: List[str], output_pptx_path: str) -> Optional[str]:
    """
    将多个已后处理的 SVG 文件合并为一个 PPTX 演示文稿。

    Args:
        svg_paths: SVG 文件路径列表（已排序、已后处理）。
        output_pptx_path: 输出 PPTX 路径。

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

    try:
        create_pptx_with_native_svg(
            svg_files=valid_paths,
            output_path=Path(output_pptx_path),
            canvas_format="ppt169",
            verbose=False,
            use_native_shapes=True,
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
