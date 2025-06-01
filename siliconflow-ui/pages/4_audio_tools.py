#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频工具页面
集成了各种音频处理工具，包括格式转换、分割合并、重命名和批量处理
"""

import streamlit as st
import sys
from pathlib import Path
import time

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入CSS样式（使用直接导入路径）
sys.path.append(str(ROOT_DIR / 'app' / 'components'))
try:
    from css import apple_css
except ImportError:
    # 如果无法导入，创建简单的替代函数
    def apple_css():
        """应用简单的CSS样式"""
        st.markdown('''
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        </style>
        ''', unsafe_allow_html=True)

# 导入音频工具模块
# 使用 try-except 确保即使某个模块导入失败也能显示其他可用工具
try:
    from tools import (
        audio_converter,
        audio_splitter_merger,
        audio_renamer,
        batch_processor
    )
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_AVAILABLE = False
    import_error = str(e)

# 导入API客户端和工具
from app.utils.api import SiliconFlowAPI
from app.utils.state import StateManager
from app.config import get_api_key

# 页面配置
st.set_page_config(
    page_title="音频工具 - SiliconFlow",
    page_icon="🎛️",
    layout="wide",
)

# 应用Apple风格CSS
apple_css()

# 页面标题
st.title("🎛️ 音频工具")

# API客户端初始化
@st.cache_resource
def init_api_client():
    """初始化API客户端（带缓存）"""
    try:
        # 初始化SiliconFlowAPI客户端
        return SiliconFlowAPI()
    except Exception as e:
        st.error(f"API初始化失败: {str(e)}")
        return None

# 状态管理
state = StateManager()

# 侧边栏 - API连接状态
with st.sidebar:
    st.subheader("API连接")
    
    # 尝试初始化API客户端
    api_client = init_api_client()
    
    # 显示API状态
    if api_client:
        st.success("✅ API已连接")
        # 缓存API状态
        state.set_api_status(True, "连接成功")
    else:
        st.error("❌ API未连接")
        st.caption("请确保已设置API密钥")
        # 缓存API状态
        state.set_api_status(False, "连接失败")
    
    # 工具信息
    st.subheader("工具信息")
    st.markdown("""
    本页面提供多种音频处理工具，包括：
    - 格式转换：支持多种格式之间的转换
    - 分割合并：切分或合并音频文件
    - 重命名：批量重命名音频文件
    - 批量处理：对多个文件进行批量操作
    
    所有工具均在本地处理文件，无需网络连接。
    """)
    
    # 依赖项检查
    st.subheader("依赖项")
    
    # 检查核心依赖
    try:
        import pydub
        st.success("✅ 核心音频库: 已安装")
    except ImportError:
        st.error("❌ 核心音频库: 未安装")
        st.caption("请安装 pydub: `pip install pydub`")
    
    # 检查 FFmpeg
    import shutil
    if shutil.which("ffmpeg"):
        st.success("✅ FFmpeg: 已安装")
    else:
        st.error("❌ FFmpeg: 未安装")
        with st.expander("安装说明"):
            st.markdown("""
            ### 安装 FFmpeg
            
            **macOS**:
            ```
            brew install ffmpeg
            ```
            
            **Windows**:
            1. 下载 [FFmpeg](https://www.ffmpeg.org/download.html)
            2. 解压并添加到系统PATH
            
            **Linux**:
            ```
            sudo apt update
            sudo apt install ffmpeg
            ```
            """)

# 主内容区域
if not TOOLS_AVAILABLE:
    st.error(f"无法加载音频工具模块: {import_error}")
    st.info("请确保已安装所有必要的依赖项，并检查项目结构是否完整。")
else:
    # 选项卡布局
    tools_tabs = st.tabs([
        "格式转换", 
        "分割和合并", 
        "重命名",
        "批量处理"
    ])
    
    # 格式转换工具
    with tools_tabs[0]:
        # 如果工具模块可用，显示工具
        try:
            audio_converter.show_audio_converter()
        except Exception as e:
            st.error(f"加载格式转换工具失败: {str(e)}")
            st.info("请确保已安装所有必要的依赖项，并检查工具模块是否正确。")
    
    # 分割和合并工具
    with tools_tabs[1]:
        try:
            audio_splitter_merger.show_audio_splitter_merger()
        except Exception as e:
            st.error(f"加载分割合并工具失败: {str(e)}")
            st.info("请确保已安装所有必要的依赖项，并检查工具模块是否正确。")
    
    # 重命名工具
    with tools_tabs[2]:
        try:
            audio_renamer.show_audio_renamer()
        except Exception as e:
            st.error(f"加载重命名工具失败: {str(e)}")
            st.info("请确保已安装所有必要的依赖项，并检查工具模块是否正确。")
    
    # 批量处理工具
    with tools_tabs[3]:
        try:
            batch_processor.show_batch_processor()
        except Exception as e:
            st.error(f"加载批量处理工具失败: {str(e)}")
            st.info("请确保已安装所有必要的依赖项，并检查工具模块是否正确。")

# 页面底部
st.divider()
st.caption("SiliconFlow 音频工具 | 所有处理均在本地进行，保证数据隐私安全")
