#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 配置管理模块
此模块负责管理应用程序的配置信息，包括API密钥、路径设置等
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()

# 添加父级目录到系统路径，确保可以导入siliconflow模块
SILICONFLOW_DIR = ROOT_DIR.parent / "siliconflow"
sys.path.append(str(SILICONFLOW_DIR))

# 音频目录
AUDIO_DIR = ROOT_DIR / "audios"
AUDIO_DIR.mkdir(exist_ok=True)

# 创建临时目录
TEMP_DIR = ROOT_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 尝试从.env文件加载配置
def load_env_config():
    """加载环境变量配置，优先从本地.env文件，其次从siliconflow目录的.env文件"""
    # 先尝试加载当前项目的.env文件
    local_env_path = ROOT_DIR / ".env"
    if local_env_path.exists():
        load_dotenv(local_env_path)
        return True
    
    # 如果本地没有，尝试加载siliconflow目录的.env文件
    siliconflow_env_path = SILICONFLOW_DIR / ".env"
    if siliconflow_env_path.exists():
        load_dotenv(siliconflow_env_path)
        return True
    
    return False

# 获取配置信息
def get_api_key():
    """获取SiliconFlow API密钥"""
    # 先尝试从环境变量获取
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        # 尝试加载.env文件
        if load_env_config():
            api_key = os.getenv("SILICONFLOW_API_KEY")
    
    return api_key

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "ogg", "flac", "m4a"]

# 应用程序信息
APP_NAME = "SiliconFlow语音工具集"
APP_VERSION = "1.0.0"
