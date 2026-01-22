# filepath: src/composer/pptx_renderer.py

import os
import subprocess
import logging
from copy import deepcopy
from typing import List, Tuple
import sys

# 仅保留 python-pptx 相关的核心依赖
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE_TYPE

import aspose.slides as slides

logger = logging.getLogger(__name__)

# ==============================================================================
# 核心工具函数
# ==============================================================================

def run_script(
    script_path: str, 
    timeout: int = 12
) -> Tuple[bool, str]:
    """
    在一个隔离的子进程中安全地执行 Python 脚本，并验证其产物。
    捕获并返回完整的错误 traceback（标准错误）。
    """
    if not os.path.isfile(script_path):
        error_msg = f"Script not found at path: {script_path}"
        logger.error(f"   -> ❌ {error_msg}")
        return False, error_msg

    python_exe = sys.executable or "python3"
    try:
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False # 不在返回非0时抛出异常
        )
        
        if result.returncode == 0:
            logger.debug(f"   -> Script {os.path.basename(script_path)} executed successfully.")
            return True, result.stdout
        else:
            # 记录更详细的错误
            error_details = result.stderr.strip()
            logger.warning(f"   -> ⚠️ Script {os.path.basename(script_path)} failed with return code {result.returncode}. Stderr:\n{error_details}")
            return False, error_details
            
    except subprocess.TimeoutExpired:
        timeout_msg = f"Script execution timed out after {timeout} seconds."
        logger.error(f"   -> ❌ {timeout_msg}")
        return False, timeout_msg
    except Exception as e:
        exec_err_msg = f"An unexpected error occurred while running the script: {e}"
        logger.error(f"   -> ❌ {exec_err_msg}", exc_info=True)
        return False, exec_err_msg

def merge_deck(ppt_files: list, output_path: str):
    """
    使用 Aspose.Slides 合并多个单页 PPTX 文件为一个完整演示文稿。
    Args:
        ppt_files: 包含单页 PPTX 文件路径的列表。
        output_path: 最终合并后文件的保存路径。
    """
    if not ppt_files:
        logger.warning("   -> No slide files provided to merge.")
        return

    logger.info(f"   -> Merging {len(ppt_files)} slides into a single presentation...")

    # 以第一个PPT为基础
    try:
        pres = slides.Presentation(ppt_files[0])

        for pptx_path in ppt_files[1:]:
            if not os.path.exists(pptx_path):
                logger.warning(f"   -> Skipping non-existent file: {pptx_path}")
                continue
            try:
                other_pres = slides.Presentation(pptx_path)
                for slide in other_pres.slides:
                    pres.slides.add_clone(slide)
            except Exception as e:
                logger.error(f"   -> ❌ Failed to merge {pptx_path}: {e}", exc_info=True)

        pres.save(output_path, slides.export.SaveFormat.PPTX)
        logger.info(f"   -> ✅ All slides merged successfully! Saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        logger.error(f"   -> ❌ Failed to create or save the final presentation: {e}", exc_info=True)