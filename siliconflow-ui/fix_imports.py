#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 导入修复脚本
此脚本用于修复所有页面文件中的导入语句
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

# 修复导入语句的正则表达式
APP_IMPORT_PATTERN = re.compile(r'from app\.(utils|components|config) import')
CONFIG_IMPORT_PATTERN = re.compile(r'from app\.config import')

# 替换模板
REPLACEMENT_TEXT = '''import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from {module} import'''

def fix_file(file_path):
    """修复单个文件中的导入语句"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复app.utils/components/config导入
    content = APP_IMPORT_PATTERN.sub(
        lambda m: REPLACEMENT_TEXT.format(module=m.group(1)) + ' ', 
        content
    )
    
    # 修复config导入
    content = CONFIG_IMPORT_PATTERN.sub(
        'from config import', 
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复文件: {file_path}")

def main():
    """主函数"""
    print("开始修复导入语句...")
    
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
