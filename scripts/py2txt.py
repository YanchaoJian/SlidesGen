"""
将 agent、workflow 目录下的所有 .py 文件以及 main.py 转换为 .txt 文件
保存到 assets/txt 目录（忽略目录层级，所有文件放在同一级）
"""
import os
import shutil
from pathlib import Path


def convert_py_to_txt(source_dirs, output_dir, include_files=None):
    """
    将指定目录下的 Python 文件转换为文本文件
    
    Args:
        source_dirs: 要扫描的源目录列表
        output_dir: 输出目录
        include_files: 额外包含的单个文件列表（如 main.py）
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 统计信息
    converted_count = 0
    file_names = set()  # 用于检测重名文件
    
    # 处理目录
    for source_dir in source_dirs:
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"⚠️  警告: 目录不存在 - {source_dir}")
            continue
        
        print(f"📂 扫描目录: {source_dir}")
        
        # 递归查找所有 .py 文件
        for py_file in source_path.rglob("*.py"):
            # 跳过 __pycache__ 目录
            if "__pycache__" in py_file.parts:
                continue
            
            # 使用源文件相对于 source_path 的完整路径作为新文件名
            # 例如: agent/parser/content_enhancer.py → agent_parser_content_enhancer.txt
            relative_path = py_file.relative_to(source_path)
            # 将路径分隔符替换为下划线
            file_stem = str(relative_path.with_suffix("")).replace(os.sep, "_")
            txt_filename = f"{file_stem}.txt"
            
            txt_file = output_path / txt_filename
            
            # 检测重名
            if txt_filename in file_names:
                print(f"   ⚠️  警告: 文件名重复 - {txt_filename}，将跳过")
                continue
            
            file_names.add(txt_filename)
            
            # 复制文件并重命名
            try:
                shutil.copy2(py_file, txt_file)
                print(f"   ✅ {relative_path} → {txt_filename}")
                converted_count += 1
            except Exception as e:
                print(f"   ❌ 转换失败 {relative_path}: {e}")
    
    # 处理单个文件
    if include_files:
        for file_path in include_files:
            py_file = Path(file_path)
            
            if not py_file.exists():
                print(f"⚠️  警告: 文件不存在 - {file_path}")
                continue
            
            # 输出到根目录，保持原文件名
            txt_filename = py_file.with_suffix(".txt").name
            txt_file = output_path / txt_filename
            
            # 检测重名
            if txt_filename in file_names:
                print(f"   ⚠️  警告: 文件名重复 - {txt_filename}，将跳过")
                continue
            
            file_names.add(txt_filename)
            
            try:
                shutil.copy2(py_file, txt_file)
                print(f"   ✅ {py_file.name} → {txt_filename}")
                converted_count += 1
            except Exception as e:
                print(f"   ❌ 转换失败 {file_path}: {e}")
    
    print(f"\n🎉 转换完成! 共转换 {converted_count} 个文件")
    print(f"📁 输出目录: {output_path.absolute()}")
    print(f"📊 文件列表已保存")


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 定义源目录
    source_directories = [
        project_root / "agent",
        project_root / "workflow"
    ]
    
    # 定义单独包含的文件
    additional_files = [
        project_root / "main.py"
    ]
    
    # 定义输出目录
    output_directory = project_root / "assets" / "txt"
    
    print("=" * 70)
    print("Python 到 Text 文件转换工具（忽略目录层级）")
    print("=" * 70)
    print(f"项目根目录: {project_root}")
    print(f"输出目录: {output_directory}")
    print("=" * 70)
    
    # 执行转换
    convert_py_to_txt(
        source_dirs=source_directories,
        output_dir=output_directory,
        include_files=additional_files
    )


if __name__ == "__main__":
    main()