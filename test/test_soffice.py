"""
测试 LibreOffice (soffice) 命令在 Windows 上的执行情况
用于诊断 PPT 转 PDF 失败的问题
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.pptx_merger import merge_svgs_to_pptx


def test_soffice_command():
    """测试 soffice 命令是否可用"""
    print("=" * 60)
    print("测试 1: 检查 soffice 命令是否可用")
    print("=" * 60)
    
    # 尝试不同命令名称
    commands_to_try = ["soffice", "soffice.exe"]
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"\n命令: {cmd}")
            print(f"  Return code: {result.returncode}")
            print(f"  Stdout: {result.stdout[:200] if result.stdout else '(empty)'}")
            print(f"  Stderr: {result.stderr[:200] if result.stderr else '(empty)'}")
            
            if result.returncode == 0 or "LibreOffice" in result.stderr:
                print(f"  [OK] {cmd} 可用!")
                return cmd
        except FileNotFoundError:
            print(f"\n命令: {cmd}")
            print(f"  [FAIL] 命令未找到 (FileNotFoundError)")
        except Exception as e:
            print(f"\n命令: {cmd}")
            print(f"  [FAIL] 错误: {e}")
    
    return None


def test_pptx_to_pdf(soffice_cmd: str):
    """测试 PPTX 转 PDF 功能"""
    print("\n" + "=" * 60)
    print("测试 2: PPTX 转 PDF 转换")
    print("=" * 60)
    
    # 创建一个简单的测试 PPTX 文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个简单的 SVG
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">
  <rect width="1280" height="720" fill="#f0f0f0"/>
  <text x="640" y="360" font-size="48" text-anchor="middle" fill="#333">Test Slide</text>
</svg>"""
        
        svg_path = os.path.join(temp_dir, "test.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"\n创建测试 SVG: {svg_path}")
        
        # 转换为 PPTX
        pptx_path = os.path.join(temp_dir, "test.pptx")
        result = merge_svgs_to_pptx([svg_path], pptx_path)
        
        if not result or not os.path.exists(pptx_path):
            print("[FAIL] SVG 转 PPTX 失败")
            return
        
        print(f"[OK] SVG 转 PPTX 成功: {pptx_path}")
        print(f"   文件大小: {os.path.getsize(pptx_path)} bytes")
        
        # 测试 PPTX 转 PDF
        pdf_output_dir = os.path.join(temp_dir, "pdf_output")
        os.makedirs(pdf_output_dir, exist_ok=True)
        
        cmd = [
            soffice_cmd,
            "--headless",
            "--convert-to", "pdf",
            pptx_path,
            "--outdir", pdf_output_dir,
        ]
        
        print(f"\n执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"\n返回码: {result.returncode}")
            print(f"Stdout: {result.stdout[:500] if result.stdout else '(empty)'}")
            print(f"Stderr: {result.stderr[:500] if result.stderr else '(empty)'}")
            
            # 检查 PDF 是否生成
            expected_pdf = os.path.join(pdf_output_dir, "test.pdf")
            if os.path.exists(expected_pdf):
                print(f"\n[OK] PDF 生成成功: {expected_pdf}")
                print(f"   文件大小: {os.path.getsize(expected_pdf)} bytes")
            else:
                print(f"\n[FAIL] PDF 未生成 (期望路径: {expected_pdf})")
                print(f"   目录内容: {os.listdir(pdf_output_dir) if os.path.exists(pdf_output_dir) else '(目录不存在)'}")
                
        except subprocess.TimeoutExpired:
            print("[FAIL] 命令超时 (60秒)")
        except Exception as e:
            print(f"[FAIL] 错误: {e}")


def test_with_real_pptx():
    """使用实际项目输出的 PPTX 测试"""
    print("\n" + "=" * 60)
    print("测试 3: 使用实际项目输出的 PPTX 测试")
    print("=" * 60)
    
    # 查找项目输出的 PPTX 文件
    output_dirs = [
        "output",
    ]
    
    test_files = []
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".pptx"):
                        test_files.append(os.path.join(root, file))
    
    if not test_files:
        print("未找到测试 PPTX 文件，跳过此测试")
        return
    
    print(f"\n找到 {len(test_files)} 个 PPTX 文件进行测试")
    
    soffice_cmd = "soffice.exe" if sys.platform == "win32" else "soffice"
    
    for pptx_file in test_files[:3]:  # 最多测试3个
        print(f"\n测试文件: {pptx_file}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cmd = [
                soffice_cmd,
                "--headless",
                "--convert-to", "pdf",
                pptx_file,
                "--outdir", temp_dir,
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                print(f"  返回码: {result.returncode}")
                
                if result.returncode != 0:
                    print(f"  Stderr: {result.stderr[:300] if result.stderr else '(empty)'}")
                
                expected_pdf = os.path.join(
                    temp_dir, 
                    Path(pptx_file).stem + ".pdf"
                )
                
                if os.path.exists(expected_pdf):
                    print(f"  [OK] PDF 生成成功")
                else:
                    print(f"  [FAIL] PDF 未生成")
                    
            except Exception as e:
                print(f"  [FAIL] 错误: {e}")


def check_libreoffice_running():
    """检查是否有 LibreOffice 进程在运行"""
    print("\n" + "=" * 60)
    print("检查: LibreOffice 进程状态")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq soffice.bin"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if "soffice.bin" in result.stdout:
            print("[WARN] 警告: 检测到 LibreOffice 正在运行")
            print("这可能会导致 headless 模式冲突")
            print("建议: 关闭所有 LibreOffice 窗口后重试")
        else:
            print("[OK] 没有检测到运行的 LibreOffice 进程")
            
    except Exception as e:
        print(f"无法检查进程: {e}")


if __name__ == "__main__":
    print("LibreOffice (soffice) 诊断工具")
    print(f"Python: {sys.version}")
    print(f"平台: {sys.platform}")
    
    # 检查进程
    if sys.platform == "win32":
        check_libreoffice_running()
    
    # 测试命令
    soffice_cmd = test_soffice_command()
    
    if soffice_cmd:
        # 测试转换
        test_pptx_to_pdf(soffice_cmd)
        
        # 测试实际文件
        test_with_real_pptx()
    else:
        print("\n[FAIL] soffice 命令不可用，请检查 LibreOffice 安装")
        print("建议: 将 LibreOffice 的 program 目录添加到系统 PATH")
