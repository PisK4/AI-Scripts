#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 增强音频播放器组件
提供带波形显示的音频播放器，增强用户体验
"""

import os
import io
import base64
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# 尝试导入AudioSegment库，如果失败则创建一个简单的异常处理机制
try:
    from pydub import AudioSegment
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    # 创建一个假的AudioSegment类，以允许应用程序加载
    class AudioSegment:
        @staticmethod
        def from_file(file_path, format=None):
            return None
        
        @staticmethod
        def from_mp3(file_path):
            return None
        
        @staticmethod
        def from_wav(file_path):
            return None

def load_audio(file_path_or_bytes):
    """
    加载音频文件并返回AudioSegment对象
    支持文件路径或二进制数据
    """
    if not AUDIO_PROCESSING_AVAILABLE:
        st.warning("音频处理功能不可用，请安装ffmpeg和音频处理依赖。")
        return None
        
    try:
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            # 从文件路径加载
            audio = AudioSegment.from_file(file_path_or_bytes)
        else:
            # 从二进制数据加载
            audio = AudioSegment.from_file(io.BytesIO(file_path_or_bytes))
        return audio
    except Exception as e:
        st.error(f"音频加载失败: {str(e)}")
        return None

def generate_waveform(audio, width=800, height=160, color="#1f77b4"):
    """
    生成音频波形图
    参数:
        audio: AudioSegment对象
        width: 图像宽度
        height: 图像高度
        color: 波形颜色
    返回:
        波形图的base64编码
    """
    if not AUDIO_PROCESSING_AVAILABLE or audio is None:
        # 如果音频处理不可用，创建一个简单的占位图
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.text(0.5, 0.5, '音频波形不可用', 
                horizontalalignment='center', verticalalignment='center', 
                transform=ax.transAxes, fontsize=12)
        ax.set_axis_off()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    try:
        # 获取音频样本数据
        samples = np.array(audio.get_array_of_samples())
        
        # 处理立体声
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
    except Exception as e:
        st.error(f"音频波形生成失败: {str(e)}")
        # 创建一个简单的错误图
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.text(0.5, 0.5, f'音频波形错误: {str(e)}', 
                horizontalalignment='center', verticalalignment='center', 
                transform=ax.transAxes, fontsize=10)
        ax.set_axis_off()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    # 计算波形数据点（降采样以提高性能）
    max_points = 2000
    if len(samples) > max_points:
        samples = samples[::len(samples) // max_points]
    
    # 创建图形
    fig, ax = plt.figure(figsize=(width/100, height/100), dpi=100), plt.axes()
    ax.plot(samples, color=color)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    # 转换为base64编码
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    
    # 返回base64编码
    return base64.b64encode(buf.read()).decode()

def enhanced_audio_player(audio_data, show_waveform=True, key=None):
    """
    增强的音频播放器组件
    参数:
        audio_data: 音频文件路径、二进制数据或AudioSegment对象
        show_waveform: 是否显示波形图
        key: Streamlit组件唯一标识
    """
    # 生成随机键以避免冲突
    if key is None:
        import random
        key = f"audio_player_{random.randint(1000, 9999)}"
    
    # 检查音频处理功能是否可用
    if not AUDIO_PROCESSING_AVAILABLE:
        st.warning("音频处理功能不可用，已切换到基本模式。要启用完整功能，请安装ffmpeg和音频处理依赖。")
        
        # 如果是文件路径，提供基本的HTML5音频播放器
        if isinstance(audio_data, str) and os.path.exists(audio_data):
            st.audio(audio_data)
        elif isinstance(audio_data, bytes):
            st.audio(audio_data)
        else:
            st.error("无法播放音频：音频数据格式无效。")
        return
    
    # 正常情况下加载音频
    audio = None
    if isinstance(audio_data, AudioSegment):
        audio = audio_data
    else:
        audio = load_audio(audio_data)
    
    if audio is None:
        st.error("无法加载音频文件")
        return
    
    # 显示标准音频播放器
    if isinstance(audio_data, (str, os.PathLike)):
        st.audio(audio_data, key=f"{key}_player")
    else:
        # 确保音频数据是字节格式
        if isinstance(audio_data, AudioSegment):
            buffer = io.BytesIO()
            audio_data.export(buffer, format="mp3")
            audio_bytes = buffer.getvalue()
        else:
            audio_bytes = audio_data
        st.audio(audio_bytes, key=f"{key}_player")
    
    # 显示波形图
    if show_waveform:
        waveform_base64 = generate_waveform(audio)
        st.markdown(
            f'<img src="data:image/png;base64,{waveform_base64}" width="100%" alt="音频波形">',
            unsafe_allow_html=True
        )
    
    # 显示音频信息
    with st.expander("音频信息", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"采样率: {audio.frame_rate} Hz")
            st.write(f"声道数: {audio.channels}")
        with col2:
            st.write(f"时长: {audio.duration_seconds:.2f} 秒")
            st.write(f"格式: {audio.channels} 声道, {audio.sample_width * 8} 位")
    
    return audio
