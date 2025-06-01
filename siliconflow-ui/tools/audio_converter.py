#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频格式转换工具
提供音频文件格式转换功能
"""

import os
import streamlit as st
import tempfile
import time
from datetime import datetime
from pathlib import Path
import sys

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入依赖项
from app.components.file_uploader import audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import BaseProgress
from app.config import AUDIO_DIR, SUPPORTED_AUDIO_FORMATS

def show_audio_converter():
    """显示音频格式转换工具"""
    st.subheader("音频格式转换")
    
    st.markdown("""
    将音频文件从一种格式转换为另一种格式。支持常见的音频格式，包括MP3、WAV、AAC、FLAC等。
    """)
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 文件上传区
        uploaded_file = audio_uploader(
            "上传要转换的音频文件",
            accept_multiple_files=False,
            help="支持的格式：" + "、".join(SUPPORTED_AUDIO_FORMATS),
            key="converter_upload"
        )
    
    with col2:
        # 转换选项
        st.subheader("转换选项")
        
        # 输出格式选择
        output_format = st.selectbox(
            "输出格式",
            options=["mp3", "wav", "ogg", "flac", "aac"],
            help="选择转换后的音频格式"
        )
        
        # 高级选项
        with st.expander("高级选项", expanded=False):
            # 音频质量
            quality = st.slider(
                "音频质量",
                min_value=1,
                max_value=10,
                value=7,
                help="音频质量越高，文件体积越大"
            )
            
            # 采样率
            sample_rate = st.select_slider(
                "采样率",
                options=[8000, 16000, 22050, 24000, 44100, 48000],
                value=44100,
                help="采样率越高，音质越好，但文件更大"
            )
    
    # 转换按钮
    if uploaded_file is not None:
        if st.button("开始转换", type="primary", key="convert_button"):
            # 导入必要的库
            try:
                from pydub import AudioSegment
            except ImportError:
                st.error("缺少必要的音频处理组件。请安装 pydub 库: `pip install pydub`")
                return
            
            # 显示处理进度
            progress = BaseProgress("转换音频")
            progress.update(0.3, "加载音频文件...")
            
            try:
                # 创建临时文件用于处理
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_input_file:
                    # 写入上传的文件到临时位置
                    temp_input_file.write(uploaded_file.getvalue())
                
                # 加载音频文件
                progress.update(0.5, "处理音频...")
                audio = AudioSegment.from_file(temp_input_file.name)
                
                # 设置采样率
                if sample_rate:
                    audio = audio.set_frame_rate(sample_rate)
                
                # 设置质量参数
                bitrate = None
                if output_format == "mp3":
                    bitrate = f"{quality * 32}k"  # 从128k到320k
                
                # 准备输出文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_base = os.path.splitext(uploaded_file.name)[0]
                output_filename = f"{filename_base}_{timestamp}.{output_format}"
                output_path = AUDIO_DIR / output_filename
                
                # 确保输出目录存在
                output_path.parent.mkdir(exist_ok=True)
                
                # 导出处理后的音频
                progress.update(0.8, "保存转换后的音频...")
                
                export_params = {"format": output_format}
                if bitrate:
                    export_params["bitrate"] = bitrate
                
                audio.export(
                    str(output_path),
                    **export_params
                )
                
                # 更新进度
                progress.update(1.0, "转换完成!")
                
                # 显示结果
                st.success(f"音频转换成功: {output_filename}")
                
                # 显示音频播放器
                st.subheader("转换结果")
                enhanced_audio_player(str(output_path), key="converted_audio")
                
                # 下载按钮
                with open(output_path, "rb") as f:
                    audio_bytes = f.read()
                
                st.download_button(
                    label=f"下载{output_format.upper()}文件",
                    data=audio_bytes,
                    file_name=output_filename,
                    mime=f"audio/{output_format}"
                )
                
                # 显示文件信息
                info = {
                    "文件名": output_filename,
                    "格式": output_format.upper(),
                    "大小": f"{os.path.getsize(output_path) / 1024:.2f} KB",
                    "时长": f"{audio.duration_seconds:.2f} 秒",
                    "采样率": f"{audio.frame_rate} Hz",
                    "声道数": audio.channels,
                    "位深度": f"{audio.sample_width * 8} bit"
                }
                
                st.subheader("文件信息")
                for key, value in info.items():
                    st.text(f"{key}: {value}")
                
            except Exception as e:
                st.error(f"音频转换失败: {str(e)}")
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_input_file.name)
                except:
                    pass
                
                # 清除进度
                progress.clear()
    
    # 使用提示
    with st.expander("使用提示", expanded=False):
        st.markdown("""
        ### 音频格式转换提示
        
        1. **关于格式选择**
           - **MP3**: 适合音乐，较小文件体积，有损压缩
           - **WAV**: 无损质量，文件较大，适合专业制作
           - **FLAC**: 无损压缩，比WAV小，保持音质
           - **OGG**: 开源格式，较好的压缩比
           - **AAC**: 比MP3更好的音质和压缩比
        
        2. **质量设置**
           - 数值越高，音质越好，但文件越大
           - MP3格式下，7对应192kbps，是音质和大小的平衡点
        
        3. **采样率**
           - 44100 Hz是CD质量
           - 更高的采样率对大多数人来说听不出差别，但文件更大
        """)
