#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 增强文件上传器组件
提供更友好的文件上传体验
"""

import os
import streamlit as st
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import SUPPORTED_AUDIO_FORMATS

def audio_uploader(label="上传音频文件", key=None, help_text=None):
    """
    增强的音频文件上传器
    参数:
        label: 上传按钮标签
        key: 组件唯一标识
        help_text: 帮助文本
    返回:
        上传的文件对象
    """
    # 生成随机键以避免冲突
    if key is None:
        import random
        key = f"audio_uploader_{random.randint(1000, 9999)}"
    
    # 显示帮助信息
    if help_text is None:
        help_text = f"支持的音频格式: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
    
    # 创建文件上传组件
    uploaded_file = st.file_uploader(
        label=label,
        type=SUPPORTED_AUDIO_FORMATS,
        help=help_text,
        key=key
    )
    
    # 增加上传提示
    if uploaded_file is None:
        st.info("👆 请点击上方按钮选择要上传的音频文件")
    
    return uploaded_file

def multi_audio_uploader(label="上传多个音频文件", key=None, help_text=None):
    """
    多文件音频上传器
    参数:
        label: 上传按钮标签
        key: 组件唯一标识
        help_text: 帮助文本
    返回:
        上传的文件对象列表
    """
    # 生成随机键以避免冲突
    if key is None:
        import random
        key = f"multi_audio_uploader_{random.randint(1000, 9999)}"
    
    # 显示帮助信息
    if help_text is None:
        help_text = f"支持的音频格式: {', '.join(SUPPORTED_AUDIO_FORMATS)}。可以按住Ctrl键选择多个文件。"
    
    # 创建文件上传组件
    uploaded_files = st.file_uploader(
        label=label,
        type=SUPPORTED_AUDIO_FORMATS,
        accept_multiple_files=True,
        help=help_text,
        key=key
    )
    
    # 增加上传提示和文件统计
    if not uploaded_files:
        st.info("👆 请点击上方按钮选择要上传的多个音频文件")
    else:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        
        # 显示文件列表
        with st.expander("查看已上传文件", expanded=False):
            for i, file in enumerate(uploaded_files):
                st.write(f"{i+1}. {file.name} ({file.size/1024:.1f} KB)")
    
    return uploaded_files
