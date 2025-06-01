#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 主页
此模块是Web应用的主入口，负责初始化应用并提供首页内容
"""

import streamlit as st
import os
import sys
from pathlib import Path

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入工具模块
from app.utils.state import StateManager
from app.utils.api import SiliconFlowAPI
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
    st.caption("© 2025 SiliconFlow语音工具集")

# 主页面内容
st.title("🏠 SiliconFlow语音工具集")

st.markdown("""
## 欢迎使用SiliconFlow语音工具集

这是一个功能强大的语音处理平台，集成了SiliconFlow API的多种语音服务。您可以轻松地进行语音识别、语音合成，以及使用多种音频处理工具。

### 主要功能

使用侧边栏导航到各个功能页面：

- **语音识别**：将音频转换为文本
- **自定义语音**：创建和管理个性化语音
- **文本转语音**：生成自然流畅的语音
- **一体化处理**：将语音识别和合成集成为完整工作流
- **工具箱**：音频格式转换、分割、合并等实用工具
""")

# 特色功能展示
st.header("特色功能")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card-container">
        <h3>🎤 语音识别</h3>
        <p>高精度的语音转文本服务，支持多种语言和场景。</p>
        <a href="/Speech_Recognition" target="_self">前往使用 →</a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-container">
        <h3>📝 文本转语音</h3>
        <p>自然流畅的语音合成，多种声音和风格选择。</p>
        <a href="/Text_to_Speech" target="_self">前往使用 →</a>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card-container">
        <h3>🧰 音频工具箱</h3>
        <p>强大的音频处理工具集，满足多种音频处理需求。</p>
        <a href="/Audio_Tools" target="_self">前往使用 →</a>
    </div>
    """, unsafe_allow_html=True)

# 系统状态
st.header("系统状态")

col1, col2 = st.columns(2)

with col1:
    st.subheader("API连接")
    if api_status["connected"]:
        st.success("API连接正常")
    else:
        st.error(f"API连接失败: {api_status['message']}")

with col2:
    st.subheader("可用服务")
    services = [
        ("语音识别", True),
        ("文本转语音", True),
        ("自定义语音", api_status["connected"]),
        ("音频处理工具", True)
    ]
    
    for service_name, is_available in services:
        if is_available:
            st.write(f"✅ {service_name}")
        else:
            st.write(f"❌ {service_name}")

# 使用指引
st.header("快速入门")
st.markdown("""
1. 确保已设置API密钥（在侧边栏检查）
2. 选择您需要使用的功能模块
3. 上传音频文件或输入文本
4. 调整参数，运行处理
5. 下载或保存结果

需要详细说明？请查看[SiliconFlow API文档](https://www.siliconflow.cn/docs)
""")

# 页脚
st.markdown("""
<footer>
    <p>SiliconFlow语音工具集 © 2025 | 基于Streamlit构建 | 苹果风格UI</p>
</footer>
""", unsafe_allow_html=True)
