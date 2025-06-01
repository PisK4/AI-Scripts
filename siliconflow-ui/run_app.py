#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 应用启动脚本
此脚本用于启动SiliconFlow语音工具集Web应用程序
"""

import os
import sys
import subprocess
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 将项目根目录添加到系统路径
sys.path.append(str(ROOT_DIR))

# 主函数
def main():
    """启动SiliconFlow语音工具集Web应用程序"""
    print("正在启动SiliconFlow语音工具集...")
    
    # 检查是否存在.env文件
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        print("\n警告: 未找到.env文件，应用可能无法正常工作")
        print("请创建.env文件，并添加您的SiliconFlow API密钥:")
        print("SILICONFLOW_API_KEY=您的API密钥\n")
    
    # 启动新的多页面Streamlit应用
    os.chdir(str(ROOT_DIR))
    subprocess.run(["streamlit", "run", "Home.py"])

# 执行主函数
if __name__ == "__main__":
    main()
