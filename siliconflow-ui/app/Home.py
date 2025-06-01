#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 主页
"""

import streamlit as st
import os
import sys
from pathlib import Path

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR.parent / "siliconflow"))

# 导入工具模块
from app.utils.state import StateManager
from app.utils.api import SiliconFlowAPI
import app.config as config
from app.config import get_api_key

# 设置页面配置 - 苹果风格界面
st.set_page_config(
    page_title="SiliconFlow语音工具集",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义CSS样式 - 苹果设计风格
def load_css_file(css_file_path):
    with open(css_file_path, 'r') as f:
        return f.read()

# 尝试加载自定义CSS文件，如果存在的话
custom_css_path = ROOT_DIR / ".streamlit" / "style.css"
if custom_css_path.exists():
    custom_css = load_css_file(custom_css_path)
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
else:
    # 使用内置的CSS作为备用
    st.markdown("""
    <style>
        /* 苹果风格的基础样式 */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
        }
        
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
        
        /* 卡片容器 */
        .card-container {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .card-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }
        
        /* 按钮样式 */
        button.stButton>button {
            border-radius: 20px !important;
            padding: 0.5rem 1.2rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        /* 页脚 */
        footer {
            margin-top: 50px;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

# 初始化会话状态
StateManager.initialize_session_state()

# 初始化API连接
@st.cache_resource(show_spinner="正在连接SiliconFlow API...")
def init_api(force_refresh=False):
    """初始化API连接，使用缓存避免重复初始化"""
    try:
        api = SiliconFlowAPI()
        # 尝试连接API
        connected, message = api.test_connection()
        
        # 更新API状态
        StateManager.set_api_status(connected, message)
        
        # 如果连接成功，获取并缓存语音列表
        if connected:
            try:
                # 主动获取语音列表
                voices = api.get_voices()
                StateManager.update_voices_list(voices)
                st.success("API连接成功！已获取语音列表")
            except Exception as e:
                st.warning(f"获取语音列表失败: {str(e)}")
        else:
            st.error(f"API连接失败: {message}")
            
        return api
    except Exception as e:
        error_msg = f"API初始化失败: {str(e)}"
        StateManager.set_api_status(False, error_msg)
        st.error(error_msg)
        return None

# 在应用启动时主动连接API
api = init_api()

# 侧边栏导航
with st.sidebar:
    st.title("SiliconFlow语音工具集")
    
    # 检查API状态
    api_key = get_api_key()
    api_status = StateManager.get_api_status()
    
    if api_key:
        # 添加一个重新连接按钮
        if st.button("重新连接API"):
            # 强制初始化API
            api = init_api(force_refresh=True)
            st.rerun()
        
        # 显示API状态
        if api_status["connected"]:
            st.success("✅ API连接正常")
        else:
            st.error(f"❌ API连接失败: {api_status['message']}")
            
            # 显示API密钥重置选项
            if st.button("重置API密钥"):
                with st.form("api_key_form"):
                    new_api_key = st.text_input("输入新的API密钥", type="password")
                    if st.form_submit_button("保存"):
                        # 保存到.env文件
                        env_path = ROOT_DIR / ".env"
                        with open(env_path, "w") as f:
                            f.write(f"SILICONFLOW_API_KEY={new_api_key}\n")
                        st.success("API密钥已更新，请刷新页面")
                        st.rerun()
    else:
        st.error("❌ 未找到API密钥")
        
        # 显示API密钥设置表单
        with st.form("api_key_form"):
            new_api_key = st.text_input("输入SiliconFlow API密钥", type="password")
            if st.form_submit_button("保存"):
                # 保存到.env文件
                env_path = ROOT_DIR / ".env"
                with open(env_path, "w") as f:
                    f.write(f"SILICONFLOW_API_KEY={new_api_key}\n")
                st.success("API密钥已保存，请刷新页面")
                st.rerun()
    
    st.markdown("---")
    
    # 创建导航菜单 - 多页面应用导航
    st.markdown("### 导航菜单")
    
    # 页脚
    st.markdown("---")
    st.caption("© 2025 SiliconFlow语音工具集")

# 导入首页模块并显示
from app.pages import home
home.show_page()
