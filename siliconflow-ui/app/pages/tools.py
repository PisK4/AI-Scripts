#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 工具箱页面
提供音频处理和转换的实用工具
"""

import os
import streamlit as st
import tempfile
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import shutil

# 使用try-except包装可能缺少依赖的导入
TOOL_DEPENDENCIES_INSTALLED = True
MISSING_DEPENDENCIES = []

try:
    from pydub import AudioSegment
except ImportError as e:
    TOOL_DEPENDENCIES_INSTALLED = False
    MISSING_DEPENDENCIES.append(str(e))

# 导入工具模块
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))

# 设置FFmpeg的路径
import os
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

from utils.state import StateManager
from utils.api import SiliconFlowAPI
from components.file_uploader import audio_uploader, multi_audio_uploader
from components.audio_player import enhanced_audio_player
from components.progress import BaseProgress
from config import AUDIO_DIR, SUPPORTED_AUDIO_FORMATS

def show_page():
    """显示工具箱页面"""
    st.title("🧰 工具箱")
    
    # 创建一个强制使用功能，方便用户在安装依赖后测试
    use_anyway = False
    
    # 检查依赖是否安装
    if not TOOL_DEPENDENCIES_INSTALLED:
        st.error("⚠️ 工具箱功能显示不可用：缺少必要的音频处理组件")
        
        st.markdown("""
        ### 缺少以下依赖：
        """)
        
        for dep in MISSING_DEPENDENCIES:
            st.code(dep, language="bash")
        
        st.markdown("""
        ### 安装指南
        
        要使用工具箱功能，您需要安装以下依赖：
        
        1. **PyAudioOp 和 FFmpeg**：音频处理所需的基础库
        
        #### 在 macOS 上安装：
        ```bash
        # 安装FFmpeg
        brew install ffmpeg
        
        # 安装PyAudio（包含pyaudioop）
        pip install pyaudio
        ```
        
        #### 在 Ubuntu/Debian 上安装：
        ```bash
        # 安装FFmpeg和开发库
        sudo apt-get update
        sudo apt-get install ffmpeg libavcodec-extra python3-dev
        
        # 安装PyAudio
        pip install pyaudio
        ```
        
        #### 在 Windows 上安装：
        1. 下载并安装 [FFmpeg](https://www.ffmpeg.org/download.html)
        2. 将FFmpeg添加到系统PATH
        3. 安装PyAudio: `pip install pyaudio`
        
        安装完成后，请重启应用程序。
        """)
        
        # 添加一个强制尝试按钮
        st.markdown("""
        ### 已经安装了依赖？
        如果您已经安装了以下依赖，但应用程序没有正确检测到，可以点击下面的按钮强制尝试使用工具箱功能。
        """)
        
        use_anyway = st.button("我已安装必要依赖，强制尝试使用")
        
        if not use_anyway:
            return
    
    st.markdown("""
    在这里，您可以使用一系列实用工具来处理和转换音频文件。
    
    选择下面的工具开始使用：
    """)
    
    # 创建工具选项卡
    tabs = st.tabs([
        "音频格式转换",
        "音频分割/合并",
        "音频重命名",
        "批量处理"
    ])
    
    # 音频格式转换
    with tabs[0]:
        show_audio_converter()
    
    # 音频分割/合并
    with tabs[1]:
        try:
            show_audio_splitter_merger()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            st.error(f"加载音频分割/合并工具时出错: {str(e)}")
            with st.expander("查看详细错误信息"):
                st.code(error_details)
            st.info("请确保您已安装了所有必要的音频处理依赖并重启应用程序。")
    
    # 音频重命名
    with tabs[2]:
        def show_audio_renamer():
            """显示音频重命名工具"""
            st.subheader("音频重命名")
            
            st.markdown("""
            批量重命名音频文件，支持自定义命名格式和前缀/后缀添加。
            """)
            
            # 上传多个音频文件
            uploaded_files = multi_audio_uploader(
                "上传要重命名的音频文件",
                key="renamer_audio_upload",
                help="上传多个音频文件进行重命名，支持拖放多个文件"
            )
            
            if uploaded_files:
                st.subheader(f"已上传 {len(uploaded_files)} 个文件")
                
                # 显示重命名选项
                st.subheader("重命名选项")
                
                # 重命名模式选择
                rename_mode = st.radio(
                    "重命名模式",
                    options=["添加前缀/后缀", "完全替换文件名", "中文拼音转换"],
                    help="选择重命名的方式"
                )
                
                if rename_mode == "添加前缀/后缀":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        prefix = st.text_input(
                            "前缀",
                            value="",
                            placeholder="输入要添加的前缀"
                        )
                    
                    with col2:
                        suffix = st.text_input(
                            "后缀",
                            value="",
                            placeholder="输入要添加的后缀（在扩展名前）"
                        )
                    
                    # 预览重命名结果
                    if uploaded_files and (prefix or suffix):
                        st.subheader("重命名预览")
                        preview_data = []
                        
                        for file in uploaded_files:
                            file_name, ext = os.path.splitext(file.name)
                            new_name = f"{prefix}{file_name}{suffix}{ext}"
                            preview_data.append({
                                "原文件名": file.name,
                                "新文件名": new_name
                            })
                        
                        st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
                
                elif rename_mode == "完全替换文件名":
                    # 自定义格式选项
                    st.markdown("使用以下占位符来定义命名格式：")
                    st.markdown("""
                    - `{num}`: 序号
                    - `{date}`: 当前日期（格式：YYYYMMDD）
                    - `{time}`: 当前时间（格式：HHMMSS）
                    - `{orig}`: 原始文件名（不含扩展名）
                    """)
                    
                    name_format = st.text_input(
                        "命名格式",
                        value="audio_{num}",
                        placeholder="如：audio_{num}_{date}"
                    )
                    
                    # 序号起始值和填充位数
                    col1, col2 = st.columns(2)
                    with col1:
                        start_num = st.number_input(
                            "序号起始值",
                            value=1,
                            min_value=0,
                            step=1
                        )
                    
                    with col2:
                        padding = st.number_input(
                            "序号填充位数",
                            value=2,
                            min_value=1,
                            max_value=10,
                            step=1,
                            help="序号将填充到0达到指定位数，如填充2时：01, 02, ..., 10"
                        )
                    
                    # 预览重命名结果
                    if uploaded_files and name_format:
                        st.subheader("重命名预览")
                        preview_data = []
                        
                        current_date = datetime.now().strftime("%Y%m%d")
                        current_time = datetime.now().strftime("%H%M%S")
                        
                        for i, file in enumerate(uploaded_files):
                            file_name, ext = os.path.splitext(file.name)
                            num = str(start_num + i).zfill(padding)
                            
                            # 替换占位符
                            new_name = name_format.replace("{num}", num)
                            new_name = new_name.replace("{date}", current_date)
                            new_name = new_name.replace("{time}", current_time)
                            new_name = new_name.replace("{orig}", file_name)
                            
                            # 添加扩展名
                            new_name = f"{new_name}{ext}"
                            
                            preview_data.append({
                                "原文件名": file.name,
                                "新文件名": new_name
                            })
                        
                        st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
                
                elif rename_mode == "中文拼音转换":
                    # 验证pypinyin是否安装
                    try:
                        import pypinyin
                        pinyin_available = True
                    except ImportError:
                        st.error("请先安装pypinyin库：`pip install pypinyin`")
                        pinyin_available = False
                    
                    if pinyin_available:
                        # 拼音格式选项
                        pinyin_style = st.radio(
                            "拼音格式",
                            options=["带音调", "不带音调", "首字母"],
                            help="选择拼音的输出格式"
                        )
                        
                        # 文字连接符
                        separator = st.text_input(
                            "连接符",
                            value="_",
                            help="用于连接拼音的字符，如'_'则结果为'ni_hao'"
                        )
                        
                        # 预览重命名结果
                        if uploaded_files:
                            st.subheader("重命名预览")
                            preview_data = []
                            
                            for file in uploaded_files:
                                file_name, ext = os.path.splitext(file.name)
                                
                                # 转换为拼音
                                if pinyin_style == "带音调":
                                    pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.TONE)
                                elif pinyin_style == "不带音调":
                                    pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.NORMAL)
                                else:  # 首字母
                                    pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.FIRST_LETTER)
                                
                                # 将拼音结果平铺并用连接符连接
                                pinyin_flat = [item[0] for item in pinyin_result]
                                new_name = separator.join(pinyin_flat) + ext
                                
                                preview_data.append({
                                    "原文件名": file.name,
                                    "新文件名": new_name
                                })
                            
                            st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
                
                # 开始重命名按钮
                if st.button("开始重命名", key="rename_audio_button"):
                    try:
                        # 创建临时目录用于处理
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 创建进度条
                            progress = BaseProgress("重命名文件中...")
                            progress.update(0.0, "开始重命名...")
                            
                            renamed_files = []
                            current_date = datetime.now().strftime("%Y%m%d")
                            current_time = datetime.now().strftime("%H%M%S")
                            
                            for i, file in enumerate(uploaded_files):
                                progress.update((i / len(uploaded_files)) * 0.8, f"处理文件 {i+1}/{len(uploaded_files)}: {file.name}")
                                
                                # 解析原文件名
                                file_name, ext = os.path.splitext(file.name)
                                new_name = ""
                                
                                # 根据选择的模式进行重命名
                                if rename_mode == "添加前缀/后缀":
                                    new_name = f"{prefix}{file_name}{suffix}{ext}"
                                
                                elif rename_mode == "完全替换文件名":
                                    num = str(start_num + i).zfill(padding)
                                    
                                    # 替换占位符
                                    new_name = name_format.replace("{num}", num)
                                    new_name = new_name.replace("{date}", current_date)
                                    new_name = new_name.replace("{time}", current_time)
                                    new_name = new_name.replace("{orig}", file_name)
                                    
                                    # 添加扩展名
                                    new_name = f"{new_name}{ext}"
                                
                                elif rename_mode == "中文拼音转换" and pinyin_available:
                                    # 转换为拼音
                                    if pinyin_style == "带音调":
                                        pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.TONE)
                                    elif pinyin_style == "不带音调":
                                        pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.NORMAL)
                                    else:  # 首字母
                                        pinyin_result = pypinyin.pinyin(file_name, style=pypinyin.FIRST_LETTER)
                                    
                                    # 将拼音结果平铺并用连接符连接
                                    pinyin_flat = [item[0] for item in pinyin_result]
                                    new_name = separator.join(pinyin_flat) + ext
                                
                                # 保存重命名后的文件
                                temp_file_path = os.path.join(temp_dir, new_name)
                                with open(temp_file_path, "wb") as f:
                                    f.write(file.getvalue())
                                
                                renamed_files.append({
                                    "original": file.name,
                                    "renamed": new_name,
                                    "path": temp_file_path
                                })
                            
                            # 创建用于下载的zip文件
                            zip_filename = f"renamed_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                            zip_path = os.path.join(temp_dir, zip_filename)
                            
                            # 创建zip文件
                            progress.update(0.9, "创建ZIP文件...")
                            shutil.make_archive(
                                os.path.splitext(zip_path)[0],  # zip文件名(不含扩展名)
                                'zip',                          # 格式
                                temp_dir,                       # 源目录
                                base_dir=None,                  # 基目录
                                verbose=False                   # 是否显示过程
                            )
                            
                            # 更新进度
                            progress.update(1.0, "重命名完成!")
                            
                            # 显示成功消息
                            st.success(f"成功重命名 {len(renamed_files)} 个文件!")
                            
                            # 显示结果表格
                            result_df = pd.DataFrame([
                                {
                                    "原文件名": item["original"],
                                    "新文件名": item["renamed"]
                                }
                                for item in renamed_files
                            ])
                            
                            st.dataframe(result_df, use_container_width=True)
                            
                            # 显示下载链接
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label="下载重命名后的文件(ZIP)",
                                    data=f.read(),
                                    file_name=zip_filename,
                                    mime="application/zip"
                                )
                    
                    except Exception as e:
                        st.error(f"重命名失败: {str(e)}")
                    finally:
                        # 清除进度
                        progress.clear()
        show_audio_renamer()
    
    # 批量处理
    with tabs[3]:
        def show_batch_processor():
            """显示音频批量处理工具"""
            st.subheader("音频批量处理")
            
            st.markdown("""
            批量处理多个音频文件，可以同时应用多种操作。
            """)
    
            # 上传多个音频文件
            uploaded_files = multi_audio_uploader(
                "上传要处理的音频文件",
                key="batch_audio_upload",
                help="上传多个音频文件进行批量处理，支持拖放多个文件"
            )
    
            if uploaded_files:
                st.subheader(f"已上传 {len(uploaded_files)} 个文件")
                
                # 显示处理选项
                st.subheader("处理选项")
                
                # 选择要应用的操作
                st.markdown("选择要应用的操作：")
        
                # 格式转换选项
                format_conversion = st.checkbox("格式转换", value=True)
        
                if format_conversion:
                    output_format = st.selectbox(
                        "输出格式",
                        options=["mp3", "wav", "flac", "ogg", "m4a"],
                        index=0,
                        help="选择转换后的音频格式"
                    )
            
                    # 如果选择mp3，显示比特率选项
                    if output_format == "mp3":
                        bitrate = st.select_slider(
                            "音质",
                            options=["低(64kbps)", "中(128kbps)", "高(192kbps)", "极高(320kbps)"],
                            value="高(192kbps)",
                            help="较高的比特率意味着更好的音质，但文件更大"
                        )
                        # 将选项转换为比特率
                        bitrate_map = {
                            "低(64kbps)": 64,
                            "中(128kbps)": 128,
                            "高(192kbps)": 192,
                            "极高(320kbps)": 320
                        }
                        bitrate_value = bitrate_map[bitrate]
        
                # 音量调整选项
                volume_adjustment = st.checkbox("音量调整")
                
                if volume_adjustment:
                    volume_change = st.slider(
                        "音量调整(分贝)",
                        min_value=-10.0,
                        max_value=10.0,
                        value=0.0,
                        step=0.5,
                        help="正值增加音量，负值降低音量。注意：过大的正值可能导致失真"
                    )
        
                # 正规化选项
                normalization = st.checkbox("音量正规化")
                
                if normalization:
                    target_db = st.slider(
                        "目标分贝值",
                        min_value=-30,
                        max_value=-1,
                        value=-3,
                        step=1,
                        help="设置音频的最大音量级别，值越高声音越大，但过高可能导致失真"
                    )
                    
                    headroom = st.slider(
                        "预留裕量分贛",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.1,
                        step=0.05,
                        help="为音频峰值提供额外的空间，避免失真"
                    )
        
                # 速度调整选项
                speed_adjustment = st.checkbox("速度调整")
                
                if speed_adjustment:
                    speed_factor = st.slider(
                        "速度因子",
                        min_value=0.5,
                        max_value=2.0,
                        value=1.0,
                        step=0.05,
                        help="大于1加快，小于1减慢。例如0.5为原速度的一半，2.0为原速度的两倍"
                    )
        
                # 前缀/后缀添加选项
                add_prefix_suffix = st.checkbox("添加前缀/后缀")
                
                if add_prefix_suffix:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        prefix = st.text_input(
                            "前缀",
                            value="",
                            placeholder="输入要添加的前缀"
                        )
                    
                    with col2:
                        suffix = st.text_input(
                            "后缀",
                            value="",
                            placeholder="输入要添加的后缀（在扩展名前）"
                        )
        
                # 开始处理按钮
                if st.button("开始批量处理", key="batch_process_button"):
                    # 验证是否选择了至少一个操作
                    if not any([format_conversion, volume_adjustment, normalization, speed_adjustment, add_prefix_suffix]):
                        st.warning("请至少选择一个处理操作")
                    else:
                        try:
                            # 创建临时目录用于处理
                            with tempfile.TemporaryDirectory() as temp_dir:
                                # 创建进度条
                                progress = BaseProgress("批量处理中...")
                                progress.update(0.0, "开始处理...")
                        
                                processed_files = []
                                
                                for i, file in enumerate(uploaded_files):
                                    file_name, ext = os.path.splitext(file.name)
                                    progress.update((i / len(uploaded_files)) * 0.8, f"处理文件 {i+1}/{len(uploaded_files)}: {file.name}")
                                    
                                    # 保存上传的文件到临时位置
                                    temp_file_path = os.path.join(temp_dir, file.name)
                                    with open(temp_file_path, "wb") as f:
                                        f.write(file.getvalue())
                                    
                                    # 加载音频文件
                                    audio = AudioSegment.from_file(temp_file_path)
                            
                                    # 应用选择的处理操作
                                    
                                    # 1. 音量调整
                                    if volume_adjustment:
                                        audio = audio + volume_change  # 分贛调整
                                    
                                    # 2. 音量正规化
                                    if normalization:
                                        # 计算当前最大分负值
                                        max_db = audio.max_dBFS
                                        # 计算需要增益的分贛值，保留裕量
                                        gain = target_db - max_db - headroom
                                        # 应用增益
                                        audio = audio.apply_gain(gain)
                                    
                                    # 3. 速度调整
                                    if speed_adjustment:
                                        # 速度变化的处理方式是改变帧率
                                        audio = audio._spawn(audio.raw_data, overrides={
                                            "frame_rate": int(audio.frame_rate * speed_factor)
                                        })
                                        # 将帧率转换回原来的帧率，但保持速度变化
                                        audio = audio.set_frame_rate(audio.frame_rate)
                            
                                    # 4. 重命名操作（添加前缀/后缀）
                                    if add_prefix_suffix:
                                        file_name = f"{prefix}{file_name}{suffix}"
                                    
                                    # 5. 格式转换
                                    if format_conversion:
                                        output_ext = f".{output_format}"
                                        # 如果是mp3格式，设置比特率
                                        export_params = {}
                                        if output_format == "mp3":
                                            export_params["bitrate"] = f"{bitrate_value}k"
                                    else:
                                        output_ext = ext
                                    
                                    # 生成输出文件名
                                    output_filename = f"{file_name}{output_ext}"
                                    output_path = os.path.join(temp_dir, output_filename)
                                    
                                    # 导出处理后的音频
                                    audio.export(
                                        output_path,
                                        format=output_format if format_conversion else output_ext.lstrip("."),
                                        **export_params if format_conversion and output_format == "mp3" else {}
                                    )
                                    
                                    # 添加到已处理文件列表
                                    processed_files.append({
                                        "original": file.name,
                                        "processed": output_filename,
                                        "path": output_path
                                    })
                        
                                # 创建用于下载的zip文件
                                progress.update(0.9, "打包处理后的文件...")
                                
                                zip_filename = f"processed_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                                zip_path = os.path.join(temp_dir, zip_filename)
                                
                                # 创建zip文件
                                shutil.make_archive(
                                    os.path.splitext(zip_path)[0],  # zip文件名(不含扩展名)
                                    'zip',                          # 格式
                                    temp_dir,                       # 源目录
                                    base_dir=None,                  # 基目录
                                    verbose=False                   # 是否显示过程
                                )
                                
                                # 更新进度
                                progress.update(1.0, "处理完成!")
                                
                                # 显示成功消息
                                st.success(f"成功处理 {len(processed_files)} 个文件!")
                                
                                # 过滤掉原始上传的文件，只保留处理后的文件
                                processed_files_paths = [f["path"] for f in processed_files]
                                
                                # 显示处理结果表格
                                result_df = pd.DataFrame([
                                    {
                                        "原文件名": item["original"],
                                        "处理后文件名": item["processed"]
                                    }
                                    for item in processed_files
                                ])
                                
                                st.dataframe(result_df, use_container_width=True)
                                
                                # 显示下载链接
                                with open(zip_path, "rb") as f:
                                    st.download_button(
                                        label="下载处理后的文件(ZIP)",
                                        data=f.read(),
                                        file_name=zip_filename,
                                        mime="application/zip"
                                    )
                        except Exception as e:
                            st.error(f"批量处理失败: {str(e)}")
                        finally:
                            # 清除进度
                            progress.clear()

        show_batch_processor()

def show_audio_converter():
    """显示音频格式转换工具"""
    # ... (其他代码保持不变)
    st.subheader("音频格式转换")
    
    st.markdown("""
    将音频文件从一种格式转换为另一种格式。支持的格式包括：
    - MP3 (高压缩比，适合一般用途)
    - WAV (无损格式，音质最佳)
    - FLAC (无损压缩，音质好且文件较小)
    - OGG (开放格式，压缩比高)
    - M4A (苹果格式，压缩比高)
    """)
    
    # 上传音频文件
    uploaded_file = audio_uploader("上传要转换的音频文件", key="converter_audio_upload")
    
    if uploaded_file:
        # 显示音频预览
        st.subheader("音频预览")
        enhanced_audio_player(uploaded_file.getvalue(), key="converter_preview_audio")
        
        # 转换选项
        st.subheader("转换选项")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 输出格式选择
            output_format = st.selectbox(
                "选择输出格式",
                options=["mp3", "wav", "flac", "ogg", "m4a"],
                help="选择要转换成的目标格式"
            )
        
        with col2:
            # 质量选择
            if output_format == "mp3":
                quality = st.select_slider(
                    "音质",
                    options=["低(64kbps)", "中(128kbps)", "高(192kbps)", "极高(320kbps)"],
                    value="高(192kbps)",
                    help="较高的比特率意味着更好的音质，但文件更大"
                )
                # 将选项转换为比特率
                bitrate_map = {
                    "低(64kbps)": 64,
                    "中(128kbps)": 128,
                    "高(192kbps)": 192,
                    "极高(320kbps)": 320
                }
                bitrate = bitrate_map[quality]
            elif output_format == "wav":
                # WAV位深度选择
                sample_width = st.select_slider(
                    "位深度",
                    options=["16位", "24位", "32位"],
                    value="16位",
                    help="位深度影响音频的动态范围，较高的位深度提供更好的质量"
                )
                # 将位深度转换为字节
                width_map = {"16位": 2, "24位": 3, "32位": 4}
                sample_width_bytes = width_map[sample_width]
            else:
                # 其他格式的通用质量设置
                compression = st.slider(
                    "压缩质量",
                    min_value=0,
                    max_value=10,
                    value=5,
                    help="0表示最高压缩率(较小文件)，10表示最佳质量(较大文件)"
                )
        
        # 采样率选择
        sample_rate = st.select_slider(
            "采样率",
            options=[8000, 16000, 22050, 24000, 44100, 48000],
            value=44100,
            help="采样率影响音频的频率范围，较高的采样率可以表示更高的音频频率"
        )
        
        # 转换按钮
        if st.button("开始转换", type="primary"):
            # 显示处理进度
            progress = BaseProgress("音频转换")
            progress.update(0.3, "正在读取音频文件...")
            
            try:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_file_path = temp_file.name
                
                # 使用pydub加载音频
                audio = AudioSegment.from_file(temp_file_path)
                
                # 更新进度
                progress.update(0.6, "正在转换音频格式...")
                
                # 调整采样率
                if audio.frame_rate != sample_rate:
                    audio = audio.set_frame_rate(sample_rate)
                
                # 调整位深度(WAV)或比特率(MP3)
                if output_format == "wav" and audio.sample_width != sample_width_bytes:
                    audio = audio.set_sample_width(sample_width_bytes)
                
                # 准备输出文件名
                output_filename = f"{os.path.splitext(uploaded_file.name)[0]}.{output_format}"
                output_path = AUDIO_DIR / output_filename
                
                # 确保输出目录存在
                output_path.parent.mkdir(exist_ok=True)
                
                # 导出转换后的音频
                export_params = {
                    "format": output_format,
                    "sample_width": audio.sample_width,
                    "frame_rate": audio.frame_rate,
                }
                
                # 添加特定格式的参数
                if output_format == "mp3":
                    export_params["bitrate"] = f"{bitrate}k"
                elif output_format in ["flac", "ogg"]:
                    export_params["compression"] = compression
                
                # 导出音频
                audio.export(
                    output_path,
                    **export_params
                )
                
                # 更新进度
                progress.update(1.0, "转换完成!")
                
                # 显示结果
                st.success(f"音频转换成功: {output_filename}")
                
                # 显示转换后的音频
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
            except Exception as e:
                st.error(f"音频转换失败: {str(e)}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
                # 清除进度
                progress.clear()

def show_audio_splitter_merger():
    """显示音频分割/合并工具"""
    st.subheader("音频分割/合并")
    
    # 创建两个子选项卡
    subtab1, subtab2 = st.tabs(["音频分割", "音频合并"])
    
    # 音频分割选项卡
    with subtab1:
        st.markdown("""
        将一个音频文件分割成多个较小的片段。您可以指定每个片段的时长或分割点。
        """)
        
        # 上传音频文件
        uploaded_file = audio_uploader("上传要分割的音频文件", key="splitter_audio_upload")
        
        if uploaded_file:
            # 显示音频预览
            st.subheader("音频预览")
            enhanced_audio_player(uploaded_file.getvalue(), key="splitter_preview_audio")
            
            # 分割选项
            st.subheader("分割选项")
            
            # 分割模式选择
            split_mode = st.radio(
                "分割模式",
                options=["按时间间隔", "按指定时间点"],
                horizontal=True,
                help="选择如何分割音频"
            )
            
            if split_mode == "按时间间隔":
                # 时间间隔分割
                interval = st.number_input(
                    "分割间隔(秒)",
                    min_value=1,
                    value=60,
                    step=1,
                    help="每个片段的时长(秒)"
                )
                
                if st.button("开始分割", type="primary"):
                    # 显示处理进度
                    progress = BaseProgress("音频分割")
                    progress.update(0.3, "正在读取音频文件...")
                    
                    try:
                        # 创建临时文件
                        with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                            temp_file.write(uploaded_file.getbuffer())
                            temp_file_path = temp_file.name
                        
                        # 使用pydub加载音频
                        audio = AudioSegment.from_file(temp_file_path)
                        
                        # 更新进度
                        progress.update(0.5, "正在分割音频...")
                        
                        # 获取音频时长(毫秒)
                        duration = len(audio)
                        
                        # 创建临时目录存放分割的音频
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 计算分割点
                            intervals = list(range(0, duration, interval * 1000))
                            if intervals[-1] < duration:
                                intervals.append(duration)
                            
                            # 分割音频
                            output_files = []
                            
                            for i in range(len(intervals) - 1):
                                # 提取片段
                                start = intervals[i]
                                end = intervals[i + 1]
                                segment = audio[start:end]
                                
                                # 保存片段
                                segment_filename = f"{os.path.splitext(uploaded_file.name)[0]}_part{i+1}.mp3"
                                segment_path = os.path.join(temp_dir, segment_filename)
                                segment.export(segment_path, format="mp3")
                                
                                # 添加到输出文件列表
                                output_files.append({
                                    "filename": segment_filename,
                                    "path": segment_path,
                                    "start": start / 1000,  # 转换为秒
                                    "end": end / 1000,      # 转换为秒
                                    "duration": (end - start) / 1000  # 转换为秒
                                })
                                
                                # 更新进度
                                progress.update(0.5 + 0.5 * (i + 1) / (len(intervals) - 1), f"已分割 {i+1}/{len(intervals)-1} 个片段...")
                            
                            # 更新进度
                            progress.update(1.0, "分割完成!")
                            
                            # 显示结果
                            st.success(f"音频分割成功，共 {len(output_files)} 个片段")
                            
                            # 创建用于下载的zip文件
                            zip_filename = f"{os.path.splitext(uploaded_file.name)[0]}_split.zip"
                            zip_path = os.path.join(temp_dir, zip_filename)
                            
                            # 创建zip文件
                            shutil.make_archive(
                                os.path.splitext(zip_path)[0],  # zip文件名(不含扩展名)
                                'zip',                          # 格式
                                temp_dir,                       # 源目录
                                base_dir=None,                  # 基目录
                                verbose=False                   # 是否显示过程
                            )
                            
                            # 显示分割结果表格
                            df = pd.DataFrame([
                                {
                                    "片段": f"片段 {i+1}",
                                    "开始时间": f"{item['start']:.2f}秒",
                                    "结束时间": f"{item['end']:.2f}秒",
                                    "时长": f"{item['duration']:.2f}秒"
                                }
                                for i, item in enumerate(output_files)
                            ])
                            
                            st.dataframe(df, use_container_width=True)
                            
                            # 显示下载链接
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label="下载所有片段(ZIP)",
                                    data=f.read(),
                                    file_name=zip_filename,
                                    mime="application/zip"
                                )
                    except Exception as e:
                        st.error(f"音频分割失败: {str(e)}")
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                        
                        # 清除进度
                        progress.clear()
            else:
                # 指定时间点分割
                st.markdown("""
                输入多个时间点(秒)，每行一个，用于指定分割位置。
                例如:
                ```
                30
                75
                120
                ```
                将在30秒、75秒和120秒处分割音频，生成4个片段。
                """)
                
                split_points_str = st.text_area(
                    "分割点(秒)",
                    height=150,
                    help="每行输入一个时间点(秒)"
                )
                
                if st.button("开始分割", type="primary"):
                    # 解析分割点
                    try:
                        split_points = []
                        for line in split_points_str.strip().split("\n"):
                            if line.strip():
                                split_points.append(float(line.strip()))
                        
                        # 确保分割点按升序排序
                        split_points.sort()
                        
                        if not split_points:
                            st.error("请输入至少一个分割点")
                            return
                    except ValueError:
                        st.error("无效的分割点格式，请确保每行只有一个数字")
                        return
                    
                    # 显示处理进度
                    progress = BaseProgress("音频分割")
                    progress.update(0.3, "正在读取音频文件...")
                    
                    try:
                        # 创建临时文件
                        with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                            temp_file.write(uploaded_file.getbuffer())
                            temp_file_path = temp_file.name
                        
                        # 使用pydub加载音频
                        audio = AudioSegment.from_file(temp_file_path)
                        
                        # 更新进度
                        progress.update(0.5, "正在分割音频...")
                        
                        # 获取音频时长(毫秒)
                        duration = len(audio)
                        
                        # 创建临时目录存放分割的音频
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 准备分割点(转换为毫秒)
                            points_ms = [0] + [int(p * 1000) for p in split_points] + [duration]
                            
                            # 分割音频
                            output_files = []
                            
                            for i in range(len(points_ms) - 1):
                                # 提取片段
                                start = points_ms[i]
                                end = points_ms[i + 1]
                                segment = audio[start:end]
                                
                                # 保存片段
                                segment_filename = f"{os.path.splitext(uploaded_file.name)[0]}_part{i+1}.mp3"
                                segment_path = os.path.join(temp_dir, segment_filename)
                                segment.export(segment_path, format="mp3")
                                
                                # 添加到输出文件列表
                                output_files.append({
                                    "filename": segment_filename,
                                    "path": segment_path,
                                    "start": start / 1000,  # 转换为秒
                                    "end": end / 1000,      # 转换为秒
                                    "duration": (end - start) / 1000  # 转换为秒
                                })
                                
                                # 更新进度
                                progress.update(0.5 + 0.5 * (i + 1) / (len(points_ms) - 1), f"已分割 {i+1}/{len(points_ms)-1} 个片段...")
                            
                            # 更新进度
                            progress.update(1.0, "分割完成!")
                            
                            # 显示结果
                            st.success(f"音频分割成功，共 {len(output_files)} 个片段")
                            
                            # 创建用于下载的zip文件
                            zip_filename = f"{os.path.splitext(uploaded_file.name)[0]}_split.zip"
                            zip_path = os.path.join(temp_dir, zip_filename)
                            
                            # 创建zip文件
                            shutil.make_archive(
                                os.path.splitext(zip_path)[0],  # zip文件名(不含扩展名)
                                'zip',                          # 格式
                                temp_dir,                       # 源目录
                                base_dir=None,                  # 基目录
                                verbose=False                   # 是否显示过程
                            )
                            
                            # 显示分割结果表格
                            df = pd.DataFrame([
                                {
                                    "片段": f"片段 {i+1}",
                                    "开始时间": f"{item['start']:.2f}秒",
                                    "结束时间": f"{item['end']:.2f}秒",
                                    "时长": f"{item['duration']:.2f}秒"
                                }
                                for i, item in enumerate(output_files)
                            ])
                            
                            st.dataframe(df, use_container_width=True)
                            
                            # 显示下载链接
                            with open(zip_path, "rb") as f:
                                st.download_button(
                                    label="下载所有片段(ZIP)",
                                    data=f.read(),
                                    file_name=zip_filename,
                                    mime="application/zip"
                                )
                    except Exception as e:
                        st.error(f"音频分割失败: {str(e)}")
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                        
                        # 清除进度
                        progress.clear()
    
    # 音频合并选项卡
    with subtab2:
        st.markdown("""
        将多个音频文件合并成一个。您可以控制合并顺序和过渡效果。
        """)
        
        # 上传多个音频文件
        uploaded_files = multi_audio_uploader(
            "上传要合并的音频文件",
            key="merger_audio_upload",
            help="上传多个音频文件进行合并，支持拖放多个文件"
        )
        
        if uploaded_files:
            st.subheader(f"已上传 {len(uploaded_files)} 个文件")
            
            # 显示合并选项
            st.subheader("合并选项")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 交叉淡入淡出选项
                crossfade = st.slider(
                    "交叉淡入淡出时长(毫秒)",
                    min_value=0,
                    max_value=3000,
                    value=0,
                    step=100,
                    help="设置音频之间的交叉淡入淡出时长，为0则表示无淡入淡出"
                )
            
            with col2:
                # 输出格式选择
                output_format = st.selectbox(
                    "输出格式",
                    options=["mp3", "wav", "flac", "ogg", "m4a"],
                    index=0,
                    help="选择合并后的音频格式"
                )
            
            # 音频间隔选项
            gap = st.slider(
                "音频间隔(毫秒)",
                min_value=0,
                max_value=5000,
                value=0,
                step=100,
                help="设置音频之间的间隔时长，为0则表示无间隔"
            )
            
            # 显示并允许重新排序上传的文件
            st.subheader("文件排序")
            st.markdown("拖动行来调整音频合并的顺序：")
            
            # 创建一个数据框来显示和排序文件
            file_data = []
            for i, file in enumerate(uploaded_files):
                file_data.append({
                    "序号": i + 1,
                    "文件名": file.name,
                    "大小": f"{file.size / 1024:.2f} KB"
                })
            
            # 创建可编辑的数据框用于排序
            df = pd.DataFrame(file_data)
            edited_df = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                disabled=["文件名", "大小"],
                key="merger_file_order"
            )
            
            # 获取新的排序
            new_order = edited_df.sort_values(by="序号").index.tolist()
            
            # 按新顺序排列文件
            ordered_files = [uploaded_files[i] for i in new_order]
            
            # 合并按钮
            if st.button("合并音频", key="merge_audio_button"):
                try:
                    # 创建临时目录用于处理
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 创建进度条
                        progress = BaseProgress("合并音频中...")
                        progress.update(0.0, "开始处理...")
                        
                        # 加载和处理音频文件
                        merged_audio = None
                        for i, file in enumerate(ordered_files):
                            progress.update((i / len(ordered_files)) * 0.8, f"处理文件 {i+1}/{len(ordered_files)}: {file.name}")
                            
                            # 保存上传的文件到临时位置
                            temp_file_path = os.path.join(temp_dir, file.name)
                            with open(temp_file_path, "wb") as f:
                                f.write(file.getvalue())
                            
                            # 加载音频文件
                            audio = AudioSegment.from_file(temp_file_path)
                            
                            # 添加到合并音频
                            if merged_audio is None:
                                merged_audio = audio
                            else:
                                # 添加间隔(如果需要)
                                if gap > 0:
                                    merged_audio += AudioSegment.silent(duration=gap)
                                
                                # 添加交叉淡入淡出(如果需要)
                                if crossfade > 0 and crossfade < len(merged_audio) and crossfade < len(audio):
                                    merged_audio = merged_audio.append(audio, crossfade=crossfade)
                                else:
                                    merged_audio += audio
                        
                        progress.update(0.9, "输出合并后的音频...")
                        
                        # 创建输出文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"merged_audio_{timestamp}.{output_format}"
                        output_path = os.path.join(temp_dir, output_filename)
                        
                        # 导出合并后的音频
                        merged_audio.export(output_path, format=output_format)
                        
                        # 更新进度
                        progress.update(1.0, "合并完成!")
                        
                        # 显示成功消息
                        st.success(f"音频合并成功！总时长: {merged_audio.duration_seconds:.2f} 秒")
                        
                        # 显示音频预览
                        st.subheader("合并后的音频预览")
                        with open(output_path, "rb") as f:
                            audio_data = f.read()
                            enhanced_audio_player(audio_data, key="merged_audio_preview")
                            
                            # 提供下载链接
                            st.download_button(
                                label="下载合并后的音频",
                                data=audio_data,
                                file_name=output_filename,
                                mime=f"audio/{output_format}"
                            )
                except Exception as e:
                    st.error(f"音频合并失败: {str(e)}")
                finally:
                    # 清除进度
                    progress.clear()
