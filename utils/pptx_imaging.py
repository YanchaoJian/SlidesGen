import os
import logging
import tempfile
import argparse
import subprocess
import shutil
import sys
from pathlib import Path

# 安装依赖: pip install python-pptx pdf2image tenacity
from pdf2image import convert_from_path
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logger = logging.getLogger(__name__)

def _get_poppler_path() -> str | None:
    """在 Windows 上查找可用的 Poppler bin 目录。"""
    if sys.platform != "win32":
        return None

    # 1. 优先使用环境变量
    env_path = os.environ.get("POPPLER_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 2. 遍历 PATH，找同时包含 pdftoppm.exe 和 pdfinfo.exe 的目录
    # 优先选择路径中带 "poppler" 的，排除明显不兼容的 "texlive"
    candidates = []
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        path_dir = path_dir.strip('"')
        if not path_dir:
            continue
        lowered = path_dir.lower()
        if "texlive" in lowered:
            continue
        bin_path = Path(path_dir)
        if (bin_path / "pdftoppm.exe").exists() and (bin_path / "pdfinfo.exe").exists():
            candidates.append(str(bin_path))

    for c in candidates:
        if "poppler" in c.lower():
            return c
    return candidates[0] if candidates else None


def _save_images_blocking(pdf_path: str, output_dir: str, dpi: int):
    """私有函数：将PDF渲染为图片并保存"""
    try:
        convert_kwargs = {}
        poppler_path = _get_poppler_path()
        if poppler_path:
            convert_kwargs["poppler_path"] = poppler_path

        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            fmt="jpeg",
            thread_count=3,
            **convert_kwargs,
        )
        
        if not images:
            raise RuntimeError("pdf2image did not return any pages from the PDF.")

        saved_files = []
        for i, img in enumerate(images):
            filename = f"slide_{i + 1:02d}.jpg"
            save_path = os.path.join(output_dir, filename)
            img.save(save_path, "JPEG", quality=90)
            saved_files.append(save_path)
        
        logger.info(f"Successfully saved {len(saved_files)} images to: {output_dir}")
        return len(saved_files)
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(RuntimeError))
def pptx_to_images(file_path: str, output_dir: str, dpi: int = 200) -> int:
    """
    将 PPT/PPTX 文件转换为一系列 JPG 图片。
    此函数依赖于 LibreOffice (soffice) 和 Poppler。
    """
    input_path = Path(file_path).resolve()
    out_dir_path = Path(output_dir).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    out_dir_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_work_dir:
        temp_work_path = Path(temp_work_dir)
        
        # 构造 LibreOffice 命令 (soffice)
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            str(input_path),
            "--outdir", str(temp_work_path),
        ]

        logger.info(f"Converting PPT to PDF: {input_path.name}...")
        
        try:
            # 增加超时以防止 soffice 卡死
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                # 打印详细错误，帮助调试
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"LibreOffice conversion failed. Stderr:\n{error_msg}")
                raise RuntimeError(f"soffice command failed with return code {result.returncode}")

        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice conversion timed out after 60 seconds.")
        except FileNotFoundError:
             raise RuntimeError("`soffice` command not found. Please ensure LibreOffice is installed and in your system's PATH.")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while running soffice: {e}")

        # 查找生成的 PDF 文件
        expected_pdf = temp_work_path / f"{input_path.stem}.pdf"
        if not expected_pdf.exists():
            raise RuntimeError("Conversion failed: PDF file was not created by LibreOffice.")

        logger.info(f"PDF generated. Rendering to images (DPI={dpi})...")

        # 同步调用图片渲染
        image_count = _save_images_blocking(str(expected_pdf), str(out_dir_path), dpi)
        return image_count

def main():
    parser = argparse.ArgumentParser(description="Convert a PPT/PPTX file to a folder of images.")
    parser.add_argument("--input_file", required=True, help="Path to the input PPT/PPTX file.")
    parser.add_argument("--output_dir", required=True, help="Path to the output folder for images.")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for the output images.")
    args = parser.parse_args()

    try:
        import time
        start_time = time.time()
        count = pptx_to_images(args.input_file, args.output_dir, args.dpi)
        duration = time.time() - start_time
        logger.info(f"Task completed! Generated {count} images in {duration:.2f} seconds.")
    except Exception as e:
        logger.error(f"Fatal error during conversion: {e}")

if __name__ == "__main__":
    main()