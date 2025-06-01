#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频重命名工具
提供音频文件批量重命名功能
"""

import os
import streamlit as st
import tempfile
import pandas as pd
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import sys
import re

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入依赖项
from app.components.file_uploader import multi_audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import BaseProgress
from app.config import AUDIO_DIR, SUPPORTED_AUDIO_FORMATS

def show_audio_renamer():
    """显示音频重命名工具"""
    st.subheader("音频重命名")
    
    st.markdown("""
    批量重命名音频文件，按照自定义规则或模式重命名。
    支持基于序号、日期时间和自定义文本的命名模式。
    """)
    
    # 文件上传区
    uploaded_files = multi_audio_uploader(
        "上传要重命名的音频文件",
        accept_multiple_files=True,
        help="支持的格式：" + "、".join(SUPPORTED_AUDIO_FORMATS),
        key="renamer_upload"
    )
    
    if uploaded_files:
        # 显示重命名选项
        st.subheader("重命名选项")
        
        # 命名模式选择
        pattern_type = st.radio(
            "命名模式",
            options=["基本模式", "高级模式"],
            horizontal=True,
            help="基本模式使用预设格式，高级模式支持自定义命名模板"
        )
        
        if pattern_type == "基本模式":
            # 基本命名选项
            col1, col2 = st.columns(2)
            
            with col1:
                # 前缀设置
                prefix = st.text_input(
                    "文件前缀",
                    value="audio",
                    help="文件名前缀，例如：'audio' 将生成 'audio_001.mp3'"
                )
            
            with col2:
                # 起始序号
                start_number = st.number_input(
                    "起始序号",
                    min_value=1,
                    value=1,
                    step=1,
                    help="文件编号的起始值"
                )
                
                # 序号位数
                padding = st.number_input(
                    "序号位数",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="编号的位数，例如：3 将生成 '001', '002', ..."
                )
            
            # 预览基本模式的命名结果
            example_name = f"{prefix}_{str(start_number).zfill(padding)}.mp3"
            st.caption(f"示例: {example_name}")
            
        else:  # 高级模式
            # 高级命名模板
            st.markdown("""
            **高级命名模板支持以下变量：**
            - `{n}` - 序号 (例如: 1, 2, 3...)
            - `{n:03d}` - 带前导零的序号 (例如: 001, 002, 003...)
            - `{date}` - 当前日期 (格式: YYYYMMDD)
            - `{time}` - 当前时间 (格式: HHMMSS)
            - `{orig_name}` - 原始文件名(不含扩展名)
            - `{ext}` - 原始文件扩展名
            """)
            
            # 命名模板输入
            template = st.text_input(
                "命名模板",
                value="{date}_{n:03d}_{orig_name}",
                help="自定义命名模板，使用上述变量构建"
            )
            
            # 预览高级模式的命名结果
            now = datetime.now()
            example_vars = {
                "n": 1,
                "date": now.strftime("%Y%m%d"),
                "time": now.strftime("%H%M%S"),
                "orig_name": "example",
                "ext": "mp3"
            }
            try:
                # 处理特殊格式化情况，如 {n:03d}
                pattern = r'\{n:([^}]+)\}'
                if re.search(pattern, template):
                    # 提取格式说明符
                    format_spec = re.search(pattern, template).group(1)
                    # 替换为普通的 {n} 以便后续格式化
                    temp_template = re.sub(pattern, '{n}', template)
                    # 手动格式化 n
                    formatted_n = format(example_vars["n"], format_spec)
                    example_vars["n"] = formatted_n
                    example_name = temp_template.format(**example_vars) + f".{example_vars['ext']}"
                else:
                    example_name = template.format(**example_vars) + f".{example_vars['ext']}"
                st.caption(f"示例: {example_name}")
            except Exception as e:
                st.error(f"模板格式错误: {str(e)}")
        
        # 保留原始扩展名选项
        keep_extension = st.checkbox(
            "保留原始文件扩展名",
            value=True,
            help="选中时将保留原始文件的扩展名，否则使用下方选择的格式"
        )
        
        # 如果不保留原始扩展名，则选择新扩展名
        if not keep_extension:
            new_extension = st.selectbox(
                "新文件扩展名",
                options=["mp3", "wav", "ogg", "flac", "m4a"],
                help="选择新的文件扩展名"
            )
        
        # 显示文件列表
        st.subheader("文件列表预览")
        
        # 准备文件列表和预览新名称
        files_data = []
        
        for i, file in enumerate(uploaded_files):
            # 获取原始文件名和扩展名
            original_name = file.name
            name_parts = os.path.splitext(original_name)
            orig_name_no_ext = name_parts[0]
            extension = name_parts[1][1:]  # 去掉点号
            
            # 准备新文件名
            if pattern_type == "基本模式":
                # 基本模式命名
                new_number = start_number + i
                new_name_no_ext = f"{prefix}_{str(new_number).zfill(padding)}"
            else:
                # 高级模式命名
                now = datetime.now()
                template_vars = {
                    "n": i + 1,
                    "date": now.strftime("%Y%m%d"),
                    "time": now.strftime("%H%M%S"),
                    "orig_name": orig_name_no_ext,
                    "ext": extension
                }
                
                try:
                    # 处理特殊格式化情况，如 {n:03d}
                    pattern = r'\{n:([^}]+)\}'
                    if re.search(pattern, template):
                        # 提取格式说明符
                        format_spec = re.search(pattern, template).group(1)
                        # 替换为普通的 {n} 以便后续格式化
                        temp_template = re.sub(pattern, '{n}', template)
                        # 手动格式化 n
                        formatted_n = format(template_vars["n"], format_spec)
                        template_vars["n"] = formatted_n
                        new_name_no_ext = temp_template.format(**template_vars)
                    else:
                        new_name_no_ext = template.format(**template_vars)
                except Exception as e:
                    st.error(f"模板应用错误: {str(e)}")
                    new_name_no_ext = f"error_in_template_{i+1}"
            
            # 确定最终扩展名
            final_extension = extension if keep_extension else new_extension
            
            # 构建完整新文件名
            new_filename = f"{new_name_no_ext}.{final_extension}"
            
            # 添加到文件数据列表
            files_data.append({
                "序号": i + 1,
                "原文件名": original_name,
                "新文件名": new_filename,
                "大小(KB)": f"{len(file.getvalue())/1024:.2f}"
            })
        
        # 显示文件列表DataFrame
        edited_df = st.data_editor(
            pd.DataFrame(files_data),
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["序号", "原文件名", "大小(KB)"],
            key="renamer_file_list"
        )
        
        # 重命名按钮
        if st.button("执行重命名", type="primary", key="rename_button"):
            # 创建临时目录用于处理
            with tempfile.TemporaryDirectory() as temp_dir:
                # 创建进度条
                progress = BaseProgress("重命名音频中...")
                progress.update(0.0, "开始处理...")
                
                try:
                    # 获取用户编辑后的新文件名
                    new_filenames = edited_df["新文件名"].tolist()
                    
                    # 检查文件名是否有冲突
                    if len(new_filenames) != len(set(new_filenames)):
                        st.error("检测到重复的文件名，请确保所有新文件名都是唯一的。")
                        progress.clear()
                        return
                    
                    # 处理每个文件
                    for i, (file, new_filename) in enumerate(zip(uploaded_files, new_filenames)):
                        progress.update((i / len(uploaded_files)) * 0.8, f"处理文件 {i+1}/{len(uploaded_files)}: {new_filename}")
                        
                        # 保存到临时目录
                        output_path = os.path.join(temp_dir, new_filename)
                        with open(output_path, "wb") as f:
                            f.write(file.getvalue())
                    
                    # 创建ZIP文件
                    progress.update(0.9, "创建ZIP文件...")
                    zip_filename = f"renamed_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    zip_path = os.path.join(temp_dir, zip_filename)
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for new_filename in new_filenames:
                            file_path = os.path.join(temp_dir, new_filename)
                            zipf.write(file_path, arcname=new_filename)
                    
                    # 更新进度
                    progress.update(1.0, "重命名完成!")
                    
                    # 显示成功消息
                    st.success(f"成功重命名 {len(uploaded_files)} 个文件!")
                    
                    # 提供ZIP下载
                    with open(zip_path, "rb") as f:
                        zip_data = f.read()
                    
                    st.download_button(
                        label="下载所有重命名文件 (ZIP)",
                        data=zip_data,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
                    
                    # 展示重命名结果
                    st.subheader("重命名结果")
                    result_df = pd.DataFrame({
                        "原文件名": [file.name for file in uploaded_files],
                        "新文件名": new_filenames
                    })
                    st.dataframe(result_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"重命名处理失败: {str(e)}")
                finally:
                    # 清除进度
                    progress.clear()
    
    # 使用提示
    with st.expander("使用提示", expanded=False):
        st.markdown("""
        ### 音频重命名提示
        
        1. **命名模式**
           - **基本模式**：简单的前缀+序号格式，适合大多数情况
           - **高级模式**：使用模板变量创建复杂的命名规则
        
        2. **高级模式技巧**
           - 使用 `{n:03d}` 可以创建带前导零的序号，如 001, 002
           - 组合使用多个变量，如 `{date}_{orig_name}_{n}`
           - 添加自定义文本，如 `recording_{n}_{time}`
        
        3. **文件扩展名**
           - 保留原始扩展名通常是最安全的选择
           - 更改扩展名不会转换音频格式，仅修改文件名
        
        4. **可编辑预览**
           - 在表格中可以手动编辑各个文件的新名称
           - 系统会检查并防止重复的文件名
        """)
