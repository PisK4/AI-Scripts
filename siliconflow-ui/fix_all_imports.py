#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 全面导入修复脚本
此脚本用于修复所有页面文件中的所有导入语句
"""

import os
import re
from pathlib import Path

# 页面文件目录
PAGES_DIR = Path(__file__).parent / "app" / "pages"
FILES_TO_FIX = [
    "integrated.py", 
    "stt.py", 
    "tts.py", 
    "voice.py"
]  # home.py和tools.py已修复

def fix_file(file_path):
    """修复单个文件中的导入语句"""
    print(f"正在修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    import_fix_added = False
    
    for line in lines:
        # 跳过已经添加的导入修复代码
        if "sys.path.append(str(Path(__file__).parent.parent.parent))" in line:
            import_fix_added = True
        
        # 替换所有的app.xxx导入
        if line.strip().startswith("from app."):
            if not import_fix_added:
                # 添加导入修复代码
                fixed_lines.extend([
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# 确保可以导入项目模块\n",
                    "sys.path.append(str(Path(__file__).parent.parent.parent))\n"
                ])
                import_fix_added = True
            
            # 替换导入语句
            line = line.replace("from app.", "from ")
        
        fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"完成修复: {file_path}")

def main():
    """主函数"""
    print("开始全面修复导入语句...")
    
    # 修复页面文件
    for filename in FILES_TO_FIX:
        file_path = PAGES_DIR / filename
        if file_path.exists():
            fix_file(file_path)
        else:
            print(f"文件不存在: {file_path}")
    
    print("导入语句修复完成!")

if __name__ == "__main__":
    main()
