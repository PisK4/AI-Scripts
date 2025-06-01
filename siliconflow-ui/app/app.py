#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - Web应用入口
此模块是Web应用的主入口，负责初始化应用并提供导航
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
import utils.state
from utils.state import StateManager
from utils.api import SiliconFlowAPI
import config
from config import get_api_key

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
    
    # 创建导航菜单 - 使用按钮替代单选按钮提升交互体验
    st.markdown("### 导航菜单")
    
    # 当前页面
    current_page = StateManager.get_current_page()
    
    # 导航项目定义
    nav_items = [
        {"page": "home", "name": "首页", "icon": "🏠"},
        {"page": "stt", "name": "语音识别", "icon": "🎤"},
        {"page": "voice", "name": "自定义语音", "icon": "🗣️"},
        {"page": "tts", "name": "文本转语音", "icon": "📝"},
        {"page": "integrated", "name": "一体化处理", "icon": "🔄"},
        {"page": "tools", "name": "工具箱", "icon": "🧰"}
    ]
    
    # 生成导航菜单
    for item in nav_items:
        if st.button(
            f"{item['icon']} {item['name']}", 
            key=f"nav_{item['page']}",
            use_container_width=True,
            type="primary" if current_page == item["page"] else "secondary"
        ):
            StateManager.set_page(item["page"])
            st.rerun()
    
    # 页面切换通过按钮点击的StateManager.set_page()实现
    # 已经在导航按钮点击时设置页面，此处不需要重复设置
    
    # 页脚
    st.markdown("---")
    st.caption("© 2025 SiliconFlow语音工具集")

# 注意：页面模块在需要时才导入，避免循环导入问题

# 根据选择的页面显示相应内容
current_page = StateManager.get_current_page()

if current_page == "home":
    from pages import home
    home.show_page()
elif current_page == "stt":
    from pages import stt
    stt.show_page()
elif current_page == "voice":
    from pages import voice
    voice.show_page()
elif current_page == "tts":
    from pages import tts
    tts.show_page()
elif current_page == "integrated":
    from pages import integrated
    integrated.show_page()
elif current_page == "tools":
    from pages import tools
    tools.show_page()
