#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 文本转语音页面
提供文本转语音功能，支持多种语音模型和参数调整
"""

import os
import streamlit as st
import tempfile
import time
from datetime import datetime
from pathlib import Path

# 导入工具模块
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.state import StateManager
from utils.api import SiliconFlowAPI
from components.audio_player import enhanced_audio_player
from components.progress import BaseProgress
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
    """显示文本转语音页面"""
    st.title("📝 文本转语音")
    
    st.markdown("""
    在这里，您可以将文本转换为语音。选择喜欢的语音模型，输入文本，我们的AI将为您生成自然流畅的语音。
    
    - 支持多种语音模型
    - 可调整语速和音调
    - 支持长文本生成
    - 生成结果可直接预览和下载
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
            return
    
    # 整理语音列表，方便用户选择
    voice_options = []
    if voices_list and "result" in voices_list:
        for voice in voices_list["result"]:
            # 提取语音信息
            voice_name = voice.get("customName", "未知")
            voice_id = voice.get("uri", "")
            
            # 添加到选项列表
            voice_options.append({
                "label": f"{voice_name}",
                "value": voice_id
            })
    
    # 创建两列布局
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("文本输入")
        
        # 文本输入区
        text_input = st.text_area(
            "输入要转换为语音的文本",
            value=st.session_state.tts_state.get("text_input", ""),
            height=200,
            placeholder="在这里输入您想要转换为语音的文本...",
            help="支持中文、英文等多种语言"
        )
        
        # 更新会话状态
        st.session_state.tts_state["text_input"] = text_input
        
        # 文本长度统计
        if text_input:
            st.caption(f"文本长度: {len(text_input)} 字符")
    
    with col2:
        st.subheader("语音设置")
        
        # 语音模型选择
        if voice_options:
            # 为语音选项添加默认选项
            all_options = [{"label": "-- 请选择语音 --", "value": ""}] + voice_options
            
            # 从格式化选项中构建标签和值的映射
            labels = [option["label"] for option in all_options]
            values = [option["value"] for option in all_options]
            
            # 获取当前选择的值
            current_value = st.session_state.tts_state.get("selected_voice", "")
            current_index = values.index(current_value) if current_value in values else 0
            
            # 创建选择框
            selected_label = st.selectbox(
                "选择语音模型",
                options=labels,
                index=current_index
            )
            
            # 获取选择的值
            selected_voice = values[labels.index(selected_label)]
            
            # 更新会话状态
            st.session_state.tts_state["selected_voice"] = selected_voice
        else:
            st.warning("未能加载语音模型列表，请检查API连接")
            selected_voice = ""
        
        # 语音参数调整
        st.subheader("参数调整")
        
        # 语速调整
        speed = st.slider(
            "语速",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.tts_state.get("speed", 1.0),
            step=0.1,
            format="%.1f",
            help="1.0 为正常语速，小于1.0变慢，大于1.0变快"
        )
        
        # 更新会话状态
        st.session_state.tts_state["speed"] = speed
        
        # 采样率选择
        sample_rate = st.select_slider(
            "采样率",
            options=[8000, 16000, 22050, 24000, 44100, 48000],
            value=st.session_state.tts_state.get("sample_rate", 24000),
            help="采样率越高，音质越好，但文件更大"
        )
        
        # 更新会话状态
        st.session_state.tts_state["sample_rate"] = sample_rate
        
        # 输出格式选择
        output_format = st.radio(
            "输出格式",
            options=["mp3", "wav"],
            horizontal=True,
            help="mp3格式文件小，wav格式无损"
        )
    
    # 生成按钮区域
    st.markdown("---")
    
    # 检查是否可以生成
    can_generate = bool(text_input and selected_voice)
    
    # 生成按钮
    if st.button("生成语音", type="primary", disabled=not can_generate):
        if not text_input:
            st.error("请输入要转换的文本")
        elif not selected_voice:
            st.error("请选择语音模型")
        else:
            # 显示处理进度
            progress = BaseProgress("生成语音")
            progress.update(0.3, "正在准备文本...")
            
            try:
                # 准备输出文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"tts_{timestamp}.{output_format}"
                output_path = AUDIO_DIR / output_filename
                
                # 确保输出目录存在
                output_path.parent.mkdir(exist_ok=True)
                
                # 更新进度
                progress.update(0.5, "正在生成语音...")
                
                # 调用API生成语音
                use_stream = len(text_input) > 500  # 长文本使用流式处理
                
                # 保存语音到文件
                api.save_speech_to_file(
                    text=text_input,
                    voice_uri=selected_voice,
                    output_path=str(output_path),
                    speed=speed,
                    sample_rate=sample_rate,
                    stream=use_stream
                )
                
                # 更新进度
                progress.update(1.0, "生成完成!")
                
                # 显示结果
                st.success(f"语音生成成功: {output_filename}")
                
                # 保存到会话状态
                st.session_state.tts_state["generated_audio"] = str(output_path)
                
                # 显示音频播放器
                st.subheader("生成结果")
                enhanced_audio_player(str(output_path), key="generated_audio")
                
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
                st.error(f"生成语音失败: {str(e)}")
            finally:
                # 清除进度
                progress.clear()
    
    # 显示历史生成结果
    if "generated_audio" in st.session_state.tts_state and st.session_state.tts_state["generated_audio"]:
        generated_audio_path = st.session_state.tts_state["generated_audio"]
        
        # 检查文件是否存在
        if os.path.exists(generated_audio_path):
            with st.expander("上次生成的语音", expanded=False):
                enhanced_audio_player(generated_audio_path, key="last_generated_audio")
    
    # 使用提示
    with st.expander("使用提示", expanded=False):
        st.markdown("""
        ### 使用提示
        
        1. **文本格式化**
           - 使用标点符号可以让语音停顿更自然
           - 过长的文本建议分段处理
        
        2. **语音选择**
           - 不同语音适合不同类型的内容
           - 您也可以上传自己的声音创建个性化语音
        
        3. **参数调整**
           - 语速: 调整说话速度，1.0为正常速度
           - 采样率: 影响音质，一般24000已有不错效果
        """)
