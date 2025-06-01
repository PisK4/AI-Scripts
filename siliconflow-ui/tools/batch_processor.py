#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频批量处理工具
提供对多个音频文件进行批量处理的功能
"""

import os
import streamlit as st
import tempfile
import pandas as pd
import zipfile
from datetime import datetime
from pathlib import Path
import sys

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入依赖项
from app.components.file_uploader import multi_audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import BaseProgress
from app.config import AUDIO_DIR, SUPPORTED_AUDIO_FORMATS

def show_batch_processor():
    """显示音频批量处理工具"""
    st.subheader("批量处理")
    
    st.markdown("""
    对多个音频文件进行批量处理，包括格式转换、音量调整、采样率修改等操作。
    """)
    
    # 文件上传区
    uploaded_files = multi_audio_uploader(
        "上传要批量处理的音频文件",
        accept_multiple_files=True,
        help="支持的格式：" + "、".join(SUPPORTED_AUDIO_FORMATS),
        key="batch_upload"
    )
    
    if uploaded_files:
        # 处理选项
        st.subheader("处理选项")
        
        # 创建选项卡用于不同处理类型
        process_tabs = st.tabs(["格式转换", "音量调整", "采样率修改", "剪裁/长度"])
        
        # 格式转换选项卡
        with process_tabs[0]:
            # 输出格式选择
            output_format = st.selectbox(
                "输出格式",
                options=["mp3", "wav", "ogg", "flac", "aac"],
                help="选择转换后的音频格式"
            )
            
            # 音频质量(针对有损格式)
            if output_format in ["mp3", "ogg", "aac"]:
                quality = st.slider(
                    "音频质量",
                    min_value=1,
                    max_value=10,
                    value=7,
                    help="音频质量越高，文件体积越大"
                )
        
        # 音量调整选项卡
        with process_tabs[1]:
            # 音量调整类型
            volume_type = st.radio(
                "调整类型",
                options=["增益调整", "音量标准化"],
                horizontal=True,
                help="选择音量调整的方式"
            )
            
            if volume_type == "增益调整":
                # 增益值
                gain = st.slider(
                    "增益(dB)",
                    min_value=-20.0,
                    max_value=20.0,
                    value=0.0,
                    step=0.5,
                    help="正值增加音量，负值减小音量"
                )
            else:
                # 标准化目标音量
                target_level = st.slider(
                    "目标音量(dB)",
                    min_value=-30.0,
                    max_value=-3.0,
                    value=-14.0,
                    step=0.5,
                    help="标准化后的目标音量，推荐-14dB"
                )
                
                # 动态范围压缩
                use_compression = st.checkbox(
                    "应用动态范围压缩",
                    value=True,
                    help="减小音量的动态范围，使声音更均衡"
                )
        
        # 采样率修改选项卡
        with process_tabs[2]:
            # 采样率选择
            sample_rate = st.select_slider(
                "采样率",
                options=[8000, 16000, 22050, 24000, 44100, 48000],
                value=44100,
                help="采样率越高，音质越好，但文件更大"
            )
            
            # 声道设置
            channels = st.radio(
                "声道",
                options=["保持原样", "单声道", "立体声"],
                horizontal=True,
                help="修改音频的声道设置"
            )
        
        # 剪裁/长度选项卡
        with process_tabs[3]:
            # 剪裁类型
            trim_type = st.radio(
                "剪裁类型",
                options=["截取指定长度", "裁剪首尾静音", "不剪裁"],
                horizontal=True,
                help="选择如何剪裁音频"
            )
            
            if trim_type == "截取指定长度":
                # 开始和结束时间
                col1, col2 = st.columns(2)
                
                with col1:
                    start_time = st.number_input(
                        "开始时间(秒)",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        help="从哪个时间点开始截取"
                    )
                
                with col2:
                    duration = st.number_input(
                        "持续时长(秒)",
                        min_value=0.1,
                        value=60.0,
                        step=0.1,
                        help="截取的音频长度，0表示截取到结尾"
                    )
            
            elif trim_type == "裁剪首尾静音":
                # 静音检测阈值
                silence_threshold = st.slider(
                    "静音阈值(dB)",
                    min_value=-70,
                    max_value=-20,
                    value=-50,
                    help="值越小，越安静的声音才会被视为静音"
                )
                
                # 首尾静音保留长度
                padding = st.slider(
                    "保留静音长度(毫秒)",
                    min_value=0,
                    max_value=1000,
                    value=100,
                    step=10,
                    help="在首尾保留的静音长度"
                )
        
        # 文件命名设置
        st.subheader("输出文件命名")
        
        # 命名模式
        naming_pattern = st.radio(
            "命名模式",
            options=["添加后缀", "完全替换"],
            horizontal=True,
            help="选择如何命名处理后的文件"
        )
        
        if naming_pattern == "添加后缀":
            # 后缀设置
            suffix = st.text_input(
                "文件名后缀",
                value="_processed",
                help="添加到原文件名后的文本，如：'file_processed.mp3'"
            )
        else:
            # 新文件名模板
            filename_template = st.text_input(
                "文件名模板",
                value="processed_{n}",
                help="新文件名模板，{n}表示序号，如：'processed_1.mp3'"
            )
        
        # 显示文件列表预览
        st.subheader("文件列表")
        
        # 准备文件列表
        files_data = [
            {
                "序号": i+1,
                "文件名": file.name,
                "大小(KB)": f"{len(file.getvalue())/1024:.2f}"
            }
            for i, file in enumerate(uploaded_files)
        ]
        
        # 显示文件列表DataFrame
        st.dataframe(
            pd.DataFrame(files_data),
            hide_index=True,
            use_container_width=True
        )
        
        # 批处理按钮
        if st.button("开始批量处理", type="primary", key="batch_process_button"):
            try:
                # 导入必要的库
                try:
                    from pydub import AudioSegment
                    from pydub.effects import normalize
                except ImportError:
                    st.error("缺少必要的音频处理组件。请安装 pydub 库: `pip install pydub`")
                    return
                
                # 创建临时目录用于处理
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 创建进度条
                    progress = BaseProgress("批量处理音频中...")
                    progress.update(0.0, "开始处理...")
                    
                    # 存储处理结果
                    processed_files = []
                    
                    # 处理每个文件
                    for i, file in enumerate(uploaded_files):
                        # 更新进度
                        progress.update(
                            (i / len(uploaded_files)) * 0.9,
                            f"处理文件 {i+1}/{len(uploaded_files)}: {file.name}"
                        )
                        
                        try:
                            # 获取原始文件名和扩展名
                            original_name = file.name
                            name_parts = os.path.splitext(original_name)
                            name_without_ext = name_parts[0]
                            
                            # 确定输出文件名
                            if naming_pattern == "添加后缀":
                                output_filename = f"{name_without_ext}{suffix}.{output_format}"
                            else:
                                output_filename = f"{filename_template.replace('{n}', str(i+1))}.{output_format}"
                            
                            # 保存上传的文件到临时位置
                            temp_input_path = os.path.join(temp_dir, f"input_{i}_{original_name}")
                            with open(temp_input_path, "wb") as f:
                                f.write(file.getvalue())
                            
                            # 加载音频文件
                            audio = AudioSegment.from_file(temp_input_path)
                            
                            # 1. 应用采样率修改
                            if process_tabs[2].name == "采样率修改" and sample_rate:
                                audio = audio.set_frame_rate(sample_rate)
                            
                            # 2. 应用声道修改
                            if process_tabs[2].name == "采样率修改" and channels != "保持原样":
                                if channels == "单声道" and audio.channels > 1:
                                    audio = audio.set_channels(1)
                                elif channels == "立体声" and audio.channels == 1:
                                    audio = audio.set_channels(2)
                            
                            # 3. 应用音量调整
                            if process_tabs[1].name == "音量调整":
                                if volume_type == "增益调整" and gain != 0:
                                    audio = audio.apply_gain(gain)
                                elif volume_type == "音量标准化":
                                    # 标准化音量
                                    audio = normalize(audio, target_level=target_level)
                                    
                                    # 应用压缩
                                    if use_compression:
                                        # 简单的压缩实现
                                        def compress_dynamic_range(audio, threshold=-20.0, ratio=4.0):
                                            """简单的动态范围压缩器"""
                                            # 将音频转换为数组
                                            samples = audio.get_array_of_samples()
                                            import numpy as np
                                            samples = np.array(samples)
                                            
                                            # 获取最大值
                                            max_sample = np.max(np.abs(samples))
                                            
                                            # 计算增益
                                            if max_sample > 0:
                                                gain = (1.0 / max_sample) * (2 ** (audio.sample_width * 8 - 1) - 1) * 0.9
                                                samples = samples * gain
                                            
                                            # 重建音频段
                                            compressed_audio = audio._spawn(samples.tobytes())
                                            return compressed_audio
                                        
                                        try:
                                            audio = compress_dynamic_range(audio)
                                        except Exception as e:
                                            st.warning(f"应用压缩失败: {str(e)}")
                            
                            # 4. 应用剪裁
                            if process_tabs[3].name == "剪裁/长度":
                                if trim_type == "截取指定长度":
                                    # 计算结束时间
                                    end_time = None
                                    if duration > 0:
                                        end_time = start_time + duration
                                    
                                    # 转换为毫秒
                                    start_ms = int(start_time * 1000)
                                    end_ms = int(end_time * 1000) if end_time is not None else len(audio)
                                    
                                    # 确保不超出音频长度
                                    end_ms = min(end_ms, len(audio))
                                    
                                    # 截取音频
                                    audio = audio[start_ms:end_ms]
                                
                                elif trim_type == "裁剪首尾静音":
                                    from pydub.silence import detect_leading_silence
                                    
                                    # 检测首尾静音
                                    def trim_silence(sound, silence_threshold=-50.0, padding_ms=100):
                                        """去除首尾静音"""
                                        # 去除开头静音
                                        start_trim = detect_leading_silence(sound, silence_threshold=silence_threshold)
                                        # 去除结尾静音
                                        end_trim = detect_leading_silence(sound.reverse(), silence_threshold=silence_threshold)
                                        
                                        # 保留指定的静音长度
                                        start_ms = max(0, start_trim - padding_ms)
                                        end_ms = max(0, len(sound) - end_trim - padding_ms)
                                        
                                        # 确保不会越界
                                        if end_ms <= start_ms:
                                            end_ms = len(sound)
                                        
                                        # 返回剪裁后的音频
                                        return sound[start_ms:end_ms]
                                    
                                    audio = trim_silence(
                                        audio,
                                        silence_threshold=silence_threshold,
                                        padding_ms=padding
                                    )
                            
                            # 确定导出参数
                            export_params = {"format": output_format}
                            
                            # 针对有损格式设置质量
                            if output_format in ["mp3", "ogg", "aac"]:
                                if output_format == "mp3":
                                    export_params["bitrate"] = f"{quality * 32}k"  # 从128k到320k
                                else:
                                    export_params["quality"] = quality / 10  # 转换为0-1范围
                            
                            # 导出处理后的音频
                            output_path = os.path.join(temp_dir, output_filename)
                            audio.export(output_path, **export_params)
                            
                            # 添加到处理结果列表
                            processed_files.append({
                                "original": original_name,
                                "processed": output_filename,
                                "path": output_path,
                                "duration": len(audio) / 1000,  # 秒
                                "size": os.path.getsize(output_path)
                            })
                            
                        except Exception as e:
                            st.error(f"处理文件 '{file.name}' 失败: {str(e)}")
                    
                    # 创建ZIP文件
                    progress.update(0.95, "创建ZIP文件...")
                    
                    if processed_files:
                        zip_filename = f"batch_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                        zip_path = os.path.join(temp_dir, zip_filename)
                        
                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for file_info in processed_files:
                                zipf.write(file_info["path"], arcname=file_info["processed"])
                        
                        # 更新进度
                        progress.update(1.0, "处理完成!")
                        
                        # 显示成功消息
                        st.success(f"成功处理 {len(processed_files)} 个文件!")
                        
                        # 创建结果摘要
                        result_df = pd.DataFrame([
                            {
                                "原文件名": info["original"],
                                "处理后文件名": info["processed"],
                                "时长(秒)": f"{info['duration']:.2f}",
                                "大小(KB)": f"{info['size']/1024:.2f}"
                            }
                            for info in processed_files
                        ])
                        
                        # 显示结果表格
                        st.subheader("处理结果")
                        st.dataframe(result_df, use_container_width=True)
                        
                        # 提供ZIP下载
                        with open(zip_path, "rb") as f:
                            zip_data = f.read()
                        
                        st.download_button(
                            label="下载所有处理后文件 (ZIP)",
                            data=zip_data,
                            file_name=zip_filename,
                            mime="application/zip"
                        )
                    else:
                        st.warning("没有成功处理任何文件。")
            
            except Exception as e:
                st.error(f"批处理失败: {str(e)}")
            finally:
                # 清除进度
                progress.clear()
    
    # 使用提示
    with st.expander("使用提示", expanded=False):
        st.markdown("""
        ### 批量处理提示
        
        1. **格式转换**
           - MP3: 较小文件，适合大多数场景
           - WAV: 无损质量，但文件较大
           - FLAC: 无损压缩，较WAV小但保持音质
           - 质量设置影响文件大小和音质
        
        2. **音量调整**
           - 增益调整: 简单地增加或减少音量
           - 音量标准化: 使所有文件音量一致
           - 动态范围压缩: 减小音量波动，让静音部分更响
        
        3. **采样率修改**
           - 44100Hz是CD质量，16000Hz适合语音
           - 降低采样率可减小文件大小
           - 提高采样率不会增加音质
        
        4. **剪裁功能**
           - 截取指定长度: 适合提取需要的部分
           - 裁剪首尾静音: 自动去除无声部分
        
        5. **命名模式**
           - 添加后缀: 保留原文件名，添加标识
           - 完全替换: 使用全新的命名模式
        """)
