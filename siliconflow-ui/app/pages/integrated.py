#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 一体化处理页面
提供语音识别、文本处理和语音合成的集成工作流
"""

import os
import streamlit as st
import tempfile
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

# 导入工具模块
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.state import StateManager
from utils.api import SiliconFlowAPI
from components.file_uploader import audio_uploader
from components.audio_player import enhanced_audio_player
from components.progress import MultiStageProgress
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import  AUDIO_DIR

# 缓存API客户端
@st.cache_resource
def get_api_client():
    """获取API客户端实例"""
    return SiliconFlowAPI()

def show_page():
    """显示一体化处理页面"""
    st.title("🔄 一体化处理")
    
    st.markdown("""
    在这里，您可以完成从语音识别到语音合成的全流程处理。
    
    **工作流程：**
    1. 上传音频文件 → 转换为文本
    2. 编辑和优化文本内容
    3. 选择语音模型 → 生成新的语音
    
    这个功能适合需要转录后再朗读、配音替换、语音翻译等场景。
    """)
    
    # 获取API客户端
    api = get_api_client()
    
    # 获取语音列表
    voices_list = StateManager.get_voices_list()
    if not voices_list:
        try:
            voices_list = api.get_voices()
            StateManager.update_voices_list(voices_list)
        except Exception as e:
            st.error(f"获取语音列表失败: {str(e)}")
    
    # 整理语音列表，方便用户选择
    voice_options = []
    if voices_list and "voices" in voices_list:
        for voice in voices_list["voices"]:
            # 提取语音信息
            voice_name = voice.get("name", "未知")
            voice_id = voice.get("id", "")
            
            # 添加到选项列表
            voice_options.append({
                "label": f"{voice_name}",
                "value": voice_id
            })
    
    # 工作流进度跟踪
    if "workflow_stage" not in st.session_state.integrated_state:
        st.session_state.integrated_state["workflow_stage"] = 1
    
    # 步骤导航
    st.progress(st.session_state.integrated_state["workflow_stage"] / 3)
    
    steps = ["1. 语音转文本", "2. 文本编辑", "3. 文本转语音"]
    st.write(f"当前步骤: **{steps[st.session_state.integrated_state['workflow_stage']-1]}**")
    
    # 根据当前阶段显示相应内容
    if st.session_state.integrated_state["workflow_stage"] == 1:
        show_step_1()
    elif st.session_state.integrated_state["workflow_stage"] == 2:
        show_step_2()
    elif st.session_state.integrated_state["workflow_stage"] == 3:
        show_step_3(voice_options)

def show_step_1():
    """显示步骤1：语音转文本"""
    st.subheader("步骤1：上传音频并转换为文本")
    
    # 上传音频文件
    uploaded_file = audio_uploader("上传音频文件", key="integrated_audio_upload")
    
    if uploaded_file:
        # 显示音频预览
        st.subheader("音频预览")
        enhanced_audio_player(uploaded_file.getvalue(), key="integrated_preview_audio")
        
        # 转录按钮
        if st.button("开始转录", type="primary"):
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name
            
            try:
                # 显示处理进度
                progress = MultiStageProgress(
                    title="一体化处理进度",
                    stages=["语音转文本", "文本编辑", "文本转语音"]
                )
                
                # 更新进度
                progress.update_stage("语音转文本", 0.3, "正在准备音频...")
                
                # 获取API客户端
                api = get_api_client()
                
                # 更新进度
                progress.update_stage("语音转文本", 0.6, "正在执行转录...")
                
                # 执行转录
                result = api.transcribe_audio(temp_file_path)
                
                # 检查结果
                if result and 'text' in result:
                    text = result['text']
                    
                    # 保存到会话状态
                    st.session_state.integrated_state["transcribed_text"] = text
                    st.session_state.integrated_state["original_audio"] = uploaded_file.name
                    st.session_state.integrated_state["workflow_stage"] = 2
                    
                    # 更新进度
                    progress.update_stage("语音转文本", 1.0, "转录完成!")
                    
                    # 清除进度显示
                    progress.clear()
                    
                    # 刷新页面以显示下一步
                    st.rerun()
                else:
                    st.error("转录失败，请检查音频文件和API密钥")
            except Exception as e:
                st.error(f"转录过程出错: {str(e)}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

def show_step_2():
    """显示步骤2：文本编辑"""
    st.subheader("步骤2：编辑和优化文本")
    
    # 检查是否有转录文本
    if "transcribed_text" not in st.session_state.integrated_state:
        st.error("未找到转录文本，请返回第一步")
        if st.button("返回第一步"):
            st.session_state.integrated_state["workflow_stage"] = 1
            st.rerun()
        return
    
    # 显示原始音频信息
    if "original_audio" in st.session_state.integrated_state:
        st.write(f"原始音频: {st.session_state.integrated_state['original_audio']}")
    
    # 文本编辑区
    edited_text = st.text_area(
        "编辑文本",
        value=st.session_state.integrated_state["transcribed_text"],
        height=300,
        help="您可以修改、优化转录的文本内容"
    )
    
    # 文本处理工具
    with st.expander("文本处理工具", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("去除标点符号"):
                import re
                cleaned_text = re.sub(r'[^\w\s]', '', edited_text)
                st.session_state.integrated_state["transcribed_text"] = cleaned_text
                st.rerun()
        
        with col2:
            if st.button("全部大写"):
                st.session_state.integrated_state["transcribed_text"] = edited_text.upper()
                st.rerun()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("全部小写"):
                st.session_state.integrated_state["transcribed_text"] = edited_text.lower()
                st.rerun()
        
        with col2:
            if st.button("添加句号"):
                import re
                # 在每个句子结尾添加句号
                processed_text = edited_text
                # 如果句子没有以句号、问号或感叹号结尾，添加句号
                processed_text = re.sub(r'([^.!?])(\s*)$', r'\1.\2', processed_text)
                # 处理句子中间的情况
                processed_text = re.sub(r'([^.!?])(\s+)([A-Z])', r'\1.\2\3', processed_text)
                
                st.session_state.integrated_state["transcribed_text"] = processed_text
                st.rerun()
    
    # 更新文本内容
    st.session_state.integrated_state["transcribed_text"] = edited_text
    
    # 导航按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("返回上一步"):
            st.session_state.integrated_state["workflow_stage"] = 1
            st.rerun()
    
    with col2:
        if st.button("继续下一步", type="primary"):
            st.session_state.integrated_state["workflow_stage"] = 3
            st.rerun()

def show_step_3(voice_options):
    """显示步骤3：文本转语音"""
    st.subheader("步骤3：选择语音模型并生成语音")
    
    # 检查是否有文本
    if "transcribed_text" not in st.session_state.integrated_state:
        st.error("未找到文本内容，请返回第一步")
        if st.button("返回第一步"):
            st.session_state.integrated_state["workflow_stage"] = 1
            st.rerun()
        return
    
    # 显示要转换的文本
    st.markdown("### 要转换的文本")
    st.write(st.session_state.integrated_state["transcribed_text"])
    
    # 语音设置
    st.markdown("### 语音设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 语音模型选择
        if voice_options:
            # 为语音选项添加默认选项
            all_options = [{"label": "-- 请选择语音 --", "value": ""}] + voice_options
            
            # 从格式化选项中构建标签和值的映射
            labels = [option["label"] for option in all_options]
            values = [option["value"] for option in all_options]
            
            # 创建选择框
            selected_label = st.selectbox(
                "选择语音模型",
                options=labels
            )
            
            # 获取选择的值
            selected_voice = values[labels.index(selected_label)]
        else:
            st.warning("未能加载语音模型列表，请检查API连接")
            selected_voice = ""
    
    with col2:
        # 语速调整
        speed = st.slider(
            "语速",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            help="1.0 为正常语速，小于1.0变慢，大于1.0变快"
        )
    
    # 输出格式选择
    output_format = st.radio(
        "输出格式",
        options=["mp3", "wav"],
        horizontal=True,
        help="mp3格式文件小，wav格式无损"
    )
    
    # 生成按钮
    if st.button("生成语音", type="primary", disabled=not selected_voice):
        if not selected_voice:
            st.error("请选择语音模型")
        else:
            # 显示处理进度
            progress = MultiStageProgress(
                title="一体化处理进度",
                stages=["语音转文本", "文本编辑", "文本转语音"]
            )
            
            # 设置前两个阶段为已完成
            progress.update_stage("语音转文本", 1.0, "已完成")
            progress.update_stage("文本编辑", 1.0, "已完成")
            progress.update_stage("文本转语音", 0.3, "正在准备...")
            
            try:
                # 准备输出文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"integrated_{timestamp}.{output_format}"
                output_path = AUDIO_DIR / output_filename
                
                # 确保输出目录存在
                output_path.parent.mkdir(exist_ok=True)
                
                # 更新进度
                progress.update_stage("文本转语音", 0.6, "正在生成语音...")
                
                # 获取API客户端
                api = get_api_client()
                
                # 调用API生成语音
                use_stream = len(st.session_state.integrated_state["transcribed_text"]) > 500  # 长文本使用流式处理
                
                # 保存语音到文件
                api.save_speech_to_file(
                    text=st.session_state.integrated_state["transcribed_text"],
                    voice_uri=selected_voice,
                    output_path=str(output_path),
                    speed=speed,
                    sample_rate=44100,  # 使用固定采样率
                    stream=use_stream
                )
                
                # 更新进度
                progress.update_stage("文本转语音", 1.0, "生成完成!")
                
                # 保存到会话状态
                st.session_state.integrated_state["output_audio"] = str(output_path)
                
                # 清除进度显示
                progress.clear()
                
                # 显示结果
                st.success(f"语音生成成功: {output_filename}")
                
                # 显示原始和生成的音频对比
                st.markdown("### 对比效果")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 原始音频")
                    if "original_audio_data" in st.session_state.integrated_state:
                        enhanced_audio_player(
                            st.session_state.integrated_state["original_audio_data"],
                            key="original_audio_compare"
                        )
                    else:
                        st.info("原始音频数据不可用")
                
                with col2:
                    st.markdown("#### 生成的语音")
                    enhanced_audio_player(str(output_path), key="generated_audio_compare")
                
                # 下载按钮
                with open(output_path, "rb") as f:
                    audio_bytes = f.read()
                
                st.download_button(
                    label=f"下载生成的{output_format.upper()}文件",
                    data=audio_bytes,
                    file_name=output_filename,
                    mime=f"audio/{output_format}"
                )
                
                # 提供重置按钮
                if st.button("开始新的处理"):
                    # 重置状态
                    for key in list(st.session_state.integrated_state.keys()):
                        if key != "workflow_stage":
                            del st.session_state.integrated_state[key]
                    
                    # 返回第一步
                    st.session_state.integrated_state["workflow_stage"] = 1
                    st.rerun()
            except Exception as e:
                st.error(f"生成语音失败: {str(e)}")
                progress.update_stage("文本转语音", 1.0, f"出错: {str(e)}")
    
    # 导航按钮
    if st.button("返回上一步"):
        st.session_state.integrated_state["workflow_stage"] = 2
        st.rerun()
