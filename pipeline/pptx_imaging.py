import os
import logging
import tempfile
import threading
import argparse
import subprocess
import shutil
import sys
from pathlib import Path

# 安装依赖: pip install python-pptx pdf2image tenacity
from pdf2image import convert_from_path
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logger = logging.getLogger(__name__)

# 限制 soffice --headless 的并发进程数。
# Windows 下即使每次调用都用独立 UserInstallation profile 避免了
# 用户配置锁冲突，系统层面（文件句柄 / 杀毒扫描 / COM 初始化）
# 在高并发时仍可能偶发失败，因此在模块级加一个闸门。
# 2 在稳和快之间取折中；如需更稳可调成 1，更快可调成 3。
_SOFFICE_MAX_CONCURRENCY = 2
_SOFFICE_SEMAPHORE = threading.Semaphore(_SOFFICE_MAX_CONCURRENCY)

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


def _save_images_blocking(pdf_path: str, output_dir: str, dpi: int) -> list[str]:
    """私有函数：将PDF渲染为图片并保存，返回生成的图片路径列表（有序）。"""
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
        return saved_files
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(RuntimeError))
def pptx_to_images(file_path: str, output_dir: str, dpi: int = 200) -> list[str]:
    """
    将 PPT/PPTX 文件转换为一系列 JPG 图片。
    返回生成图片的绝对路径列表（按页序）。
    此函数依赖于 LibreOffice (soffice) 和 Poppler。
    """
    input_path = Path(file_path).resolve()
    out_dir_path = Path(output_dir).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    out_dir_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_work_dir:
        temp_work_path = Path(temp_work_dir)

        # 为本次调用分配独立的 LibreOffice user profile，避免多个 soffice
        # 进程共享 ~/.config/libreoffice 时因 profile 锁定而失败
        # （表现为 stderr "Unknown error"）。
        profile_dir = temp_work_path / "lo_profile"
        profile_dir.mkdir()
        user_installation = profile_dir.as_uri()  # file:///... 跨平台

        # 构造 LibreOffice 命令 (soffice)
        # 注意：-env:UserInstallation 必须位于其他参数之前。
        cmd = [
            "soffice",
            f"-env:UserInstallation={user_installation}",
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--nodefault",
            "--nofirststartwizard",
            "--convert-to", "pdf",
            str(input_path),
            "--outdir", str(temp_work_path),
        ]

        logger.info(f"Converting PPT to PDF: {input_path.name}...")

        try:
            # 限流：同一时刻最多 _SOFFICE_MAX_CONCURRENCY 个 soffice 进程。
            # 只包裹 subprocess.run 本身，后续 pdf2image 渲染不受此闸门限制。
            with _SOFFICE_SEMAPHORE:
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
        saved_files = _save_images_blocking(str(expected_pdf), str(out_dir_path), dpi)
        return saved_files

def main():
    parser = argparse.ArgumentParser(description="Convert a PPT/PPTX file to a folder of images.")
    parser.add_argument("--input_file", required=True, help="Path to the input PPT/PPTX file.")
    parser.add_argument("--output_dir", required=True, help="Path to the output folder for images.")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for the output images.")
    args = parser.parse_args()

    try:
        import time
        start_time = time.time()
        files = pptx_to_images(args.input_file, args.output_dir, args.dpi)
        duration = time.time() - start_time
        logger.info(f"Task completed! Generated {len(files)} images in {duration:.2f} seconds.")
    except Exception as e:
        logger.error(f"Fatal error during conversion: {e}")

if __name__ == "__main__":
    main()