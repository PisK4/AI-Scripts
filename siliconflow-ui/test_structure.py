#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这个脚本用来测试多页面应用结构并诊断问题
"""

import os
import sys
from pathlib import Path
import subprocess

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

def print_section(title):
    """打印带有分隔线的标题"""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "-"))
    print("="*50 + "\n")

def check_file_structure():
    """检查文件结构是否符合Streamlit多页面应用要求"""
    print_section("检查文件结构")
    
    # 检查主文件
    home_file = ROOT_DIR / "Home.py"
    if home_file.exists():
        print(f"✅ 主页文件存在: {home_file}")
    else:
        print(f"❌ 主页文件不存在: {home_file}")
    
    # 检查pages目录
    pages_dir = ROOT_DIR / "pages"
    if pages_dir.exists() and pages_dir.is_dir():
        print(f"✅ pages目录存在: {pages_dir}")
        # 列出pages目录下的文件
        print("\n页面文件:")
        for file in pages_dir.glob("*.py"):
            print(f"  - {file.name}")
    else:
        print(f"❌ pages目录不存在或不是目录: {pages_dir}")

def check_streamlit_config():
    """检查Streamlit配置文件"""
    print_section("检查Streamlit配置")
    
    config_dir = ROOT_DIR / ".streamlit"
    config_file = config_dir / "config.toml"
    
    if config_file.exists():
        print(f"✅ Streamlit配置文件存在: {config_file}")
        # 显示配置文件内容
        print("\n配置文件内容:")
        with open(config_file, "r") as f:
            print(f.read())
    else:
        print(f"❌ Streamlit配置文件不存在: {config_file}")

def check_module_imports():
    """检查模块导入是否正确"""
    print_section("检查模块导入")
    
    # 检查主页导入
    try:
        sys.path.append(str(ROOT_DIR))
        import Home
        print("✅ 成功导入主页模块")
    except Exception as e:
        print(f"❌ 导入主页模块失败: {str(e)}")
    
    # 检查是否能导入app模块
    try:
        sys.path.append(str(ROOT_DIR / "app"))
        from app.utils.state import StateManager
        print("✅ 成功导入StateManager模块")
    except Exception as e:
        print(f"❌ 导入StateManager模块失败: {str(e)}")

def main():
    """主函数，运行所有检查"""
    print_section("多页面应用结构诊断")
    print(f"项目根目录: {ROOT_DIR}")
    
    # 运行检查
    check_file_structure()
    check_streamlit_config()
    check_module_imports()
    
    # 打印修复建议
    print_section("修复建议")
    print("""
1. 确保Home.py和pages/目录位于同一级，并且pages目录中包含所有页面文件

2. Streamlit多页面应用的文件命名规则：
   - 主页文件必须命名为Home.py (首字母大写，没有数字前缀)
   - pages目录中的文件应该使用数字前缀，如1_xxx.py、2_xxx.py
   - 文件名中的空格会被转换为下划线显示在侧边栏

3. 检查所有页面是否有正确的导入路径:
   - 确保在每个页面文件中都添加了正确的sys.path.append
   - 验证所有导入使用一致的路径
    """)

if __name__ == "__main__":
    main()
