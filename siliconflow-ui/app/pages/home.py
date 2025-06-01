#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 首页模块
显示应用程序的主页和功能概览
"""

import streamlit as st
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.state import StateManager

def show_page():
    """显示首页"""
    st.markdown('<h1 class="main-title">欢迎使用 SiliconFlow 语音工具集</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    这是一个功能强大的语音处理平台，基于SiliconFlow API，帮助您轻松实现语音识别、文本转语音和自定义语音等功能。
    
    使用这个工具，您可以：
    - 将音频转换为文本
    - 使用AI朗读您的文本
    - 上传音频创建个性化语音
    - 完成从音频转文本到创建个性化语音的全流程
    
    🚀 选择下方任意功能卡片开始使用，或使用左侧导航栏切换功能。
    """)
    
    # 功能卡片布局
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="card-container">
                <div class="card-title">🎤 语音识别</div>
                <p>将音频文件转换为文本，支持单个或批量处理。</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("开始语音识别", key="start_stt"):
                StateManager.set_page("stt")
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="card-container">
                <div class="card-title">🗣️ 自定义语音</div>
                <p>上传您的声音样本，创建个性化语音模型。</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("创建自定义语音", key="start_voice"):
                StateManager.set_page("voice")
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="card-container">
                <div class="card-title">📝 文本转语音</div>
                <p>使用AI朗读您的文本，支持多种语音和参数调整。</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("开始文本转语音", key="start_tts"):
                StateManager.set_page("tts")
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="card-container">
                <div class="card-title">🔄 一体化处理</div>
                <p>完成从音频转文本到创建自定义语音的全流程。</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("开始一体化处理", key="start_integrated"):
                StateManager.set_page("integrated")
                st.rerun()
    
    # 系统状态概览
    st.markdown("---")
    st.subheader("系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_status = StateManager.get_api_status()
        status_color = "green" if api_status["connected"] else "red"
        status_text = "已连接" if api_status["connected"] else "未连接"
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
            <span style="font-weight: bold;">API状态:</span> 
            <span style="color: {status_color};">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        voices_count = len(StateManager.get_voices_list())
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
            <span style="font-weight: bold;">可用语音:</span> {voices_count}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # 这里可以显示其他系统信息，例如版本号等
        st.markdown("""
        <div style="padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
            <span style="font-weight: bold;">版本:</span> 1.0.0
        </div>
        """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("""
    <footer>
        <p>SiliconFlow语音工具集 - 让语音处理变得简单</p>
    </footer>
    """, unsafe_allow_html=True)
