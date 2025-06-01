#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频分割/合并工具
提供音频文件的分割和合并功能
"""

import os
import streamlit as st
import tempfile
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入依赖项
from app.components.file_uploader import audio_uploader, multi_audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import BaseProgress
from app.config import AUDIO_DIR, SUPPORTED_AUDIO_FORMATS

def show_audio_splitter_merger():
    """显示音频分割/合并工具"""
    st.subheader("音频分割/合并")
    
    # 创建子选项卡
    subtabs = st.tabs(["音频分割", "音频合并"])
    
    # 音频分割选项卡
    with subtabs[0]:
        show_audio_splitter()
    
    # 音频合并选项卡
    with subtabs[1]:
        show_audio_merger()

def show_audio_splitter():
    """显示音频分割工具"""
    st.markdown("""
    将一个音频文件分割成多个小段。您可以按时间间隔、静音检测或自定义点分割。
    """)
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 文件上传区
        uploaded_file = audio_uploader(
            "上传要分割的音频文件",
            accept_multiple_files=False,
            help="支持的格式：" + "、".join(SUPPORTED_AUDIO_FORMATS),
            key="splitter_upload"
        )
    
    with col2:
        # 分割选项
        st.subheader("分割选项")
        
        # 分割类型
        split_type = st.radio(
            "分割方式",
            options=["等时间间隔", "静音检测", "自定义时间点"],
            help="选择如何分割音频"
        )
        
        if split_type == "等时间间隔":
            # 分割间隔设置
            interval = st.number_input(
                "分割间隔(秒)",
                min_value=1,
                value=60,
                help="每个分段的时长"
            )
        elif split_type == "静音检测":
            # 静音检测参数
            silence_threshold = st.slider(
                "静音阈值(dB)",
                min_value=-70,
                max_value=-20,
                value=-40,
                help="值越小，越安静的声音才会被视为静音"
            )
            min_silence_len = st.number_input(
                "最小静音长度(毫秒)",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="持续多长时间的静音才会被识别为分割点"
            )
        elif split_type == "自定义时间点":
            # 自定义时间点输入
            time_points_str = st.text_area(
                "时间点列表(秒)",
                placeholder="例如：30, 75, 120\n每行一个时间点，或用逗号分隔",
                help="音频将在这些时间点被分割"
            )
        
        # 输出格式选择
        output_format = st.selectbox(
            "输出格式",
            options=["mp3", "wav", "ogg", "flac"],
            help="选择分割后的音频格式"
        )
    
    # 分割按钮
    if uploaded_file is not None:
        if st.button("开始分割", type="primary", key="split_button"):
            # 导入必要的库
            try:
                from pydub import AudioSegment
                from pydub.silence import split_on_silence, detect_silence
            except ImportError:
                st.error("缺少必要的音频处理组件。请安装 pydub 库: `pip install pydub`")
                return
            
            # 显示处理进度
            progress = BaseProgress("分割音频")
            progress.update(0.1, "加载音频文件...")
            
            try:
                # 创建临时文件用于处理
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_input_file:
                    # 写入上传的文件到临时位置
                    temp_input_file.write(uploaded_file.getvalue())
                
                # 加载音频文件
                progress.update(0.3, "处理音频...")
                audio = AudioSegment.from_file(temp_input_file.name)
                
                # 准备时间点
                time_points = []
                
                if split_type == "等时间间隔":
                    # 根据间隔生成时间点
                    total_duration = len(audio) / 1000  # 毫秒转换为秒
                    time_points = list(range(interval, int(total_duration), interval))
                elif split_type == "静音检测":
                    # 检测静音
                    progress.update(0.4, "检测静音...")
                    silences = detect_silence(
                        audio, 
                        min_silence_len=min_silence_len,
                        silence_thresh=silence_threshold
                    )
                    # 使用静音中点作为分割点
                    for start, end in silences:
                        mid_point = (start + end) / 2 / 1000  # 转换为秒
                        time_points.append(mid_point)
                elif split_type == "自定义时间点":
                    # 解析用户输入的时间点
                    if time_points_str:
                        # 替换换行符为逗号
                        time_points_str = time_points_str.replace('\n', ',')
                        try:
                            # 解析时间点
                            time_points = [float(t.strip()) for t in time_points_str.split(',') if t.strip()]
                            # 排序并去重
                            time_points = sorted(list(set(time_points)))
                        except ValueError:
                            st.error("时间点格式无效。请使用数字，以逗号或换行分隔。")
                            progress.clear()
                            return
                
                # 创建临时目录存放分割结果
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 准备分割
                    progress.update(0.5, "分割音频...")
                    
                    # 添加起始点和结束点
                    time_points = [0] + time_points + [len(audio) / 1000]
                    
                    # 存储分割结果
                    output_files = []
                    
                    # 根据时间点分割
                    for i in range(len(time_points) - 1):
                        progress.update(0.5 + (i / (len(time_points) - 1)) * 0.4, f"正在分割第 {i+1}/{len(time_points)-1} 段...")
                        
                        # 计算毫秒时间点
                        start_ms = int(time_points[i] * 1000)
                        end_ms = int(time_points[i+1] * 1000)
                        
                        # 提取音频段
                        segment = audio[start_ms:end_ms]
                        
                        # 生成输出文件名
                        output_filename = f"split_{i+1}_{uploaded_file.name.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
                        output_path = os.path.join(temp_dir, output_filename)
                        
                        # 导出分段
                        segment.export(output_path, format=output_format)
                        
                        # 添加到结果列表
                        output_files.append({
                            "path": output_path,
                            "filename": output_filename,
                            "duration": len(segment) / 1000  # 秒
                        })
                    
                    # 更新进度
                    progress.update(0.95, "准备下载...")
                    
                    # 创建ZIP文件
                    import zipfile
                    zip_filename = f"split_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    zip_path = os.path.join(temp_dir, zip_filename)
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for file_info in output_files:
                            zipf.write(file_info["path"], arcname=file_info["filename"])
                    
                    # 更新进度
                    progress.update(1.0, "分割完成!")
                    
                    # 显示结果
                    st.success(f"音频分割成功！共 {len(output_files)} 个分段")
                    
                    # 显示分段列表
                    st.subheader("分段列表")
                    
                    # 创建数据表格
                    segments_df = pd.DataFrame([
                        {
                            "分段序号": i+1,
                            "开始时间(秒)": time_points[i],
                            "结束时间(秒)": time_points[i+1],
                            "时长(秒)": file_info["duration"]
                        }
                        for i, file_info in enumerate(output_files)
                    ])
                    
                    st.dataframe(segments_df)
                    
                    # 提供ZIP下载
                    with open(zip_path, "rb") as f:
                        zip_data = f.read()
                    
                    st.download_button(
                        label="下载所有分段 (ZIP)",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
                    
                    # 提供单独下载和预览
                    st.subheader("预览和单独下载")
                    
                    for i, file_info in enumerate(output_files):
                        with st.expander(f"分段 {i+1}: {file_info['duration']:.2f} 秒"):
                            # 加载音频数据
                            with open(file_info["path"], "rb") as f:
                                audio_data = f.read()
                            
                            # 显示预览
                            enhanced_audio_player(audio_data, key=f"segment_preview_{i}")
                            
                            # 提供下载
                            st.download_button(
                                label=f"下载分段 {i+1}",
                                data=audio_data,
                                file_name=file_info["filename"],
                                mime=f"audio/{output_format}"
                            )
            
            except Exception as e:
                st.error(f"音频分割失败: {str(e)}")
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_input_file.name)
                except:
                    pass
                
                # 清除进度
                progress.clear()

def show_audio_merger():
    """显示音频合并工具"""
    st.markdown("""
    将多个音频文件合并成一个。您可以调整合并顺序、设置间隔和淡入淡出效果。
    """)
    
    # 文件上传区
    uploaded_files = multi_audio_uploader(
        "上传要合并的音频文件",
        accept_multiple_files=True,
        help="支持的格式：" + "、".join(SUPPORTED_AUDIO_FORMATS) + "。文件将按上传顺序合并。",
        key="merger_upload"
    )
    
    if uploaded_files:
        # 合并选项
        st.subheader("合并选项")
        
        # 两列布局用于选项
        col1, col2 = st.columns(2)
        
        with col1:
            # 输出格式选择
            output_format = st.selectbox(
                "输出格式",
                options=["mp3", "wav", "ogg", "flac"],
                help="选择合并后的音频格式"
            )
        
        with col2:
            # 间隔设置
            gap = st.number_input(
                "音频间隔(毫秒)",
                min_value=0,
                max_value=5000,
                value=500,
                step=100,
                help="每个音频之间的静音间隔"
            )
            
            # 交叉淡入淡出
            crossfade = st.number_input(
                "交叉淡入淡出(毫秒)",
                min_value=0,
                max_value=5000,
                value=0,
                step=100,
                help="设置大于0的值启用交叉淡入淡出效果"
            )
        
        # 显示文件列表
        st.subheader("文件列表和排序")
        st.caption("拖拽行以调整合并顺序")
        
        # 准备文件列表的DataFrame
        files_data = [
            {
                "序号": i+1,
                "文件名": file.name,
                "大小(KB)": f"{len(file.getvalue())/1024:.2f}"
            }
            for i, file in enumerate(uploaded_files)
        ]
        
        # 显示可编辑的DataFrame
        edited_df = st.data_editor(
            pd.DataFrame(files_data),
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="merger_file_list",
            column_config={
                "序号": st.column_config.NumberColumn(
                    "序号",
                    help="拖动调整顺序",
                    min_value=1,
                    max_value=len(uploaded_files),
                    step=1
                ),
                "文件名": st.column_config.TextColumn(
                    "文件名",
                    help="音频文件名"
                ),
                "大小(KB)": st.column_config.TextColumn(
                    "大小",
                    help="文件大小"
                )
            }
        )
        
        # 获取新的排序
        new_order = edited_df.sort_values(by="序号").index.tolist()
        
        # 按新顺序排列文件
        ordered_files = [uploaded_files[i] for i in new_order]
        
        # 合并按钮
        if st.button("合并音频", key="merge_audio_button"):
            try:
                # 导入必要的库
                try:
                    from pydub import AudioSegment
                except ImportError:
                    st.error("缺少必要的音频处理组件。请安装 pydub 库: `pip install pydub`")
                    return
                
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
