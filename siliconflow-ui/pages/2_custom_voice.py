#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 简易自定义语音页面
允许用户只用一段音频、一个名称和文本即可创建个性化语音模型
"""

import os
import streamlit as st
import tempfile
import time
import sys
import base64
import re
import json
import requests
import wave
import math
import shutil
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="简易自定义语音 - SiliconFlow语音工具集",
    page_icon="🎙️",
    layout="wide"
)

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入工具模块
from app.utils.state import StateManager
from app.utils.api import SiliconFlowAPI
from app.config import get_api_key
from app.components.file_uploader import audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import MultiStageProgress

# 加载自定义CSS样式
def load_css_file(css_file_path):
    with open(css_file_path, 'r') as f:
        return f.read()

# 加载苹果风格CSS
custom_css_path = ROOT_DIR / ".streamlit" / "style.css"
if custom_css_path.exists():
    custom_css = load_css_file(custom_css_path)
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# 初始化会话状态
StateManager.initialize_session_state()

# 初始化自定义语音状态
if "custom_voice_state" not in st.session_state:
    st.session_state.custom_voice_state = {
        "voice_name": "",
        "reading_text": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始",
        "created_voice_id": None,
        "created_voice_name": None,
        "success": False,
        "audio_chunks": [],         # 存储分割后的音频片段
        "chunk_transcriptions": [], # 存储每个片段的转录文本
        "selected_chunk_index": None, # 用户选择的片段索引
        "processing_stage": "upload"  # 当前处理阶段: upload, segment, select, create
    }

# 初始化API连接
@st.cache_resource(show_spinner="正在连接SiliconFlow API...")
def init_api():
    return SiliconFlowAPI()

# 检查API连接
def check_api_connection():
    api = init_api()
    connected, message = api.test_connection()
    StateManager.set_api_status(connected, message)
    return connected, message, api

# 显示API状态
def show_api_status():
    status = st.session_state.get('api_status', {'connected': False, 'message': '未连接'})
    if status['connected']:
        st.success(f"API状态: {status['message']}")
        return True
    else:
        st.error(f"API状态: {status['message']}")
        with st.expander("查看API密钥配置帮助"):
            st.code("""
# 在项目根目录创建.env文件，内容如下：
SILICONFLOW_API_KEY=your_api_key_here
            """)
        return False

# 音频分割函数
def split_audio_into_chunks(audio_path, chunk_length_seconds=10):
    """
    将WAV音频文件分割成多个固定长度的片段
    如果文件小于5MB，则不进行切割
    
    参数:
        audio_path: 音频文件路径
        chunk_length_seconds: 每个片段的长度(秒)，默认10秒
        
    返回:
        temp_chunk_files: 临时文件路径列表
    """
    # 检查文件大小，如果小于5MB则不进行切割
    file_size = os.path.getsize(audio_path)
    if file_size < 5 * 1024 * 1024:  # 5MB = 5 * 1024 * 1024 字节
        st.info(f"音频文件大小为 {file_size / (1024 * 1024):.2f}MB，小于5MB，无需切割")
        return [audio_path]
        
    # 创建临时目录存储分割的文件
    temp_dir = tempfile.mkdtemp()
    
    # 将上传的文件先转换为wav格式
    temp_wav_path = os.path.join(temp_dir, "temp_audio.wav")
    
    # 如果不是wav文件，使用ffmpeg转换
    file_ext = os.path.splitext(audio_path)[1].lower()
    if file_ext != ".wav":
        try:
            # 尝试使用ffmpeg如果存在
            os.system(f'ffmpeg -i "{audio_path}" "{temp_wav_path}" -y')
            # 更新音频路径为转换后的文件
            audio_path = temp_wav_path
        except Exception as e:
            st.error(f"转换音频格式失败: {str(e)}")
            # 如果转换失败，保留原始音频文件
            shutil.copy(audio_path, temp_wav_path)
            audio_path = temp_wav_path
    else:
        # 如果已经是wav文件，直接复制
        shutil.copy(audio_path, temp_wav_path)
        audio_path = temp_wav_path
    
    # 读取WAV文件信息
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            comp_type = wav_file.getcomptype()
            comp_name = wav_file.getcompname()
            
            # 计算每个片段的帧数
            frames_per_chunk = int(chunk_length_seconds * framerate)
            total_chunks = math.ceil(n_frames / frames_per_chunk)
            
            # 分割并保存每个片段
            temp_chunk_files = []
            for i in range(total_chunks):
                # 创建片段文件路径
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
                
                # 定位到当前片段开始位置
                wav_file.setpos(i * frames_per_chunk)
                
                # 读取当前片段的数据
                # 如果是最后一个片段，可能会少于指定的帧数
                remaining_frames = n_frames - (i * frames_per_chunk)
                current_chunk_frames = min(frames_per_chunk, remaining_frames)
                frames = wav_file.readframes(current_chunk_frames)
                
                # 创建新的WAV文件存储片段
                with wave.open(chunk_path, 'wb') as chunk_file:
                    chunk_file.setnchannels(n_channels)
                    chunk_file.setsampwidth(sample_width)
                    chunk_file.setframerate(framerate)
                    chunk_file.setcomptype(comp_type, comp_name)
                    chunk_file.writeframes(frames)
                
                temp_chunk_files.append(chunk_path)
    
    except Exception as e:
        # 如果分割失败，至少返回原始文件作为单个片段
        st.warning(f"音频分割失败: {str(e)}\n返回原始文件作为单个片段")
        temp_chunk_files = [audio_path]
    
    return temp_chunk_files

# 转录音频片段为文本
def transcribe_audio_chunk(api, chunk_path):
    """
    将音频片段转录为文本
    
    参数:
        api: SiliconFlowAPI实例
        chunk_path: 音频片段路径
        
    返回:
        transcription: 转录结果文本
    """
    try:
        result = api.transcribe_audio(chunk_path)
        if result and 'text' in result:
            return result['text']
        return ""
    except Exception as e:
        st.warning(f"转录音频片段出错: {str(e)}")
        return ""

# 上传自定义语音样本
def upload_custom_voice(api_key, audio_data, custom_name, text):
    """上传自定义语音样本到SiliconFlow API"""
    url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 将音频转换为Base64编码
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    audio_data_uri = f'data:audio/mpeg;base64,{audio_base64}'
    
    # 准备请求数据
    data = {
        'audio': audio_data_uri,
        'customName': custom_name,
        'text': text,
        'model': 'FunAudioLLM/CosyVoice2-0.5B'
    }
    
    # 发送请求
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": "响应解析失败", "raw": response.text}
    else:
        return {"error": f"请求失败: {response.status_code}", "message": response.text}

# 主页面内容
st.title("🎙️ 简易自定义语音")

# 检查API连接
connected, message, api = check_api_connection()
if not show_api_status():
    st.stop()

st.markdown("""
## 一键创建个性化语音模型
只需三步，即可创建属于你自己的语音模型：
1. 上传一段你的语音音频（5-10秒）
2. 为语音输入一个独特的名称
3. 提供音频所对应的文字内容
""")

# 如果已经成功创建语音，显示成功信息和跳转按钮
if st.session_state.custom_voice_state.get("success", False):
    st.success(f"自定义语音 '{st.session_state.custom_voice_state['created_voice_name']}' 创建成功了！")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("创建新的自定义语音", use_container_width=True):
            # 重置状态
            st.session_state.custom_voice_state = {
                "voice_name": "",
                "reading_text": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始",
                "created_voice_id": None,
                "created_voice_name": None,
                "success": False,
                "audio_chunks": [],
                "chunk_transcriptions": [],
                "selected_chunk_index": None,
                "processing_stage": "upload"
            }
            st.rerun()
    
    with col2:
        if st.button("使用这个语音生成音频", type="primary", use_container_width=True):
            # 跳转到文本转语音页面
            st.switch_page("3_text_to_speech.py")
    
    st.stop()

# 处理不同的阶段
processing_stage = st.session_state.custom_voice_state["processing_stage"]

# 第一阶段: 上传音频文件
if processing_stage == "upload":
    st.subheader("第一步: 上传音频文件")
    st.info("上传您的语音音频，系统将自动将其分割为多个10秒的片段，并进行转录")
    
    # 语音名称输入
    voice_name = st.text_input(
        "语音名称 *",
        value=st.session_state.custom_voice_state["voice_name"],
        placeholder="为您的语音起个名字，如小明的声音",
        help="名称将用于标识您的自定义语音模型"
    )
    
    # 音频文件上传
    st.markdown("⤴️ **上传您的语音样本**")
    uploaded_file = audio_uploader(
        "选择一个音频文件",
        key="simple_voice_upload",
        help_text="上传您的语音音频文件，将自动分割并转录"
    )
    
    if st.button("下一步: 开始处理音频", type="primary"):
        if not voice_name:
            st.error("请输入语音名称")
        elif not uploaded_file:
            st.error("请上传语音样本文件")
        else:
            # 更新语音名称
            st.session_state.custom_voice_state["voice_name"] = voice_name
            
            # 创建进度指示器
            progress_stages = [
                {"name": "处理音频文件", "weight": 0.3},
                {"name": "分割音频", "weight": 0.3},
                {"name": "转录音频片段", "weight": 0.4}
            ]
            progress = MultiStageProgress(progress_stages, "处理音频中...")
            
            try:
                # 处理上传的音频文件
                st.info("正在处理音频文件...")
                progress.update_stage(0, 0.5)
                
                # 保存上传的音频文件
                temp_dir = tempfile.mkdtemp()
                temp_audio_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 更新进度
                st.info("音频处理完成")
                progress.update_stage(0, 1.0)
                
                # 分割音频
                st.info("正在将音频分割为10秒片段...")
                progress.update_stage(1, 0.3)
                chunk_files = split_audio_into_chunks(temp_audio_path)
                st.info(f"分割完成，共{len(chunk_files)}个片段")
                progress.update_stage(1, 1.0)
                
                # 转录每个片段
                st.info("正在转录音频片段...")
                progress.update_stage(2, 0.2)
                
                # 转录每个片段
                transcriptions = []
                total_chunks = len(chunk_files)
                for i, chunk_file in enumerate(chunk_files):
                    progress_value = 0.2 + 0.8 * ((i + 1) / total_chunks)
                    st.info(f"正在转录第 {i+1}/{total_chunks} 个片段...")
                    transcription = transcribe_audio_chunk(api, chunk_file)
                    transcriptions.append(transcription)
                    progress.update_stage(2, progress_value)
                
                st.info("所有片段转录完成")
                progress.update_stage(2, 1.0)
                
                # 存储结果到会话状态
                st.session_state.custom_voice_state["audio_chunks"] = chunk_files
                st.session_state.custom_voice_state["chunk_transcriptions"] = transcriptions
                st.session_state.custom_voice_state["processing_stage"] = "select"
                
                # 重新加载页面显示片段选择界面
                time.sleep(1)  # 等待进度条显示完成
                st.rerun()
                
            except Exception as e:
                st.error(f"处理音频时出错: {str(e)}")
                st.exception(e)

# 第二阶段: 选择片段
elif processing_stage == "select":
    st.subheader("第二步: 选择用于自定义语音的片段")
    st.info("选择一个转录效果最好的片段来创建你的自定义语音模型")
    
    # 显示所有片段及其转录文本
    chunk_files = st.session_state.custom_voice_state["audio_chunks"]
    transcriptions = st.session_state.custom_voice_state["chunk_transcriptions"]
    
    # 创建选择片段的框
    selected_index = st.radio(
        "选择一个片段",
        options=list(range(len(chunk_files))),
        format_func=lambda i: f"片段 {i+1} (时长约 10 秒)",
        index=0 if st.session_state.custom_voice_state["selected_chunk_index"] is None else st.session_state.custom_voice_state["selected_chunk_index"]
    )
    
    # 显示选中片段的音频和转录文本
    if 0 <= selected_index < len(chunk_files):
        st.subheader(f"片段 {selected_index+1} 预览")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.audio(chunk_files[selected_index])
        
        with col2:
            # 显示转录文本并允许编辑
            transcription = st.text_area(
                "转录文本",
                value=transcriptions[selected_index],
                height=100,
                key=f"transcription_{selected_index}"
            )
            # 更新编辑后的转录文本
            transcriptions[selected_index] = transcription
            st.session_state.custom_voice_state["chunk_transcriptions"] = transcriptions
    
    # 更新选中的片段索引
    st.session_state.custom_voice_state["selected_chunk_index"] = selected_index
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("返回上一步", use_container_width=True):
            st.session_state.custom_voice_state["processing_stage"] = "upload"
            st.rerun()
    
    with col2:
        if st.button("下一步: 创建语音模型", type="primary", use_container_width=True):
            # 检查选中片段的转录文本是否为空
            if not transcriptions[selected_index].strip():
                st.error("选中片段的转录文本不能为空")
            else:
                st.session_state.custom_voice_state["reading_text"] = transcriptions[selected_index]
                st.session_state.custom_voice_state["processing_stage"] = "create"
                st.rerun()

# 第三阶段: 创建自定义语音
elif processing_stage == "create":
    st.subheader("第三步: 创建自定义语音模型")
    
    # 显示所选片段的预览
    selected_index = st.session_state.custom_voice_state["selected_chunk_index"]
    chunk_files = st.session_state.custom_voice_state["audio_chunks"]
    
    if 0 <= selected_index < len(chunk_files):
        st.info(f"您选择了片段 {selected_index+1} 作为自定义语音的样本")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.audio(chunk_files[selected_index])
        
        with col2:
            # 显示最终文本
            reading_text = st.text_area(
                "最终文字内容",
                value=st.session_state.custom_voice_state["reading_text"],
                height=100
            )
            st.session_state.custom_voice_state["reading_text"] = reading_text
    
    # 名称确认
    voice_name = st.text_input(
        "确认语音名称",
        value=st.session_state.custom_voice_state["voice_name"]
    )
    st.session_state.custom_voice_state["voice_name"] = voice_name
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("返回选择片段", use_container_width=True):
            st.session_state.custom_voice_state["processing_stage"] = "select"
            st.rerun()
    
    with col2:
        create_button = st.button("创建语音模型", type="primary", use_container_width=True)

# 处理创建语音按钮逻辑
if processing_stage == "create" and create_button:
    # 检查必填字段
    selected_index = st.session_state.custom_voice_state["selected_chunk_index"]
    if not voice_name:
        st.error("请输入语音名称")
    elif not st.session_state.custom_voice_state["reading_text"]:
        st.error("请输入文字内容")
    else:
        # 清理名称，去除特殊字符
        sanitized_name = re.sub(r'[^a-zA-Z0-9_\-\u4e00-\u9fff]', '_', voice_name)
        sanitized_name = sanitized_name[:64]  # 限制名称长度
        
        # 获取选中的音频片段路径
        chunk_files = st.session_state.custom_voice_state["audio_chunks"]
        selected_audio_path = chunk_files[selected_index]
        reading_text = st.session_state.custom_voice_state["reading_text"]
        
        # 创建进度指示器
        progress_stages = [
            {"name": "处理音频片段", "weight": 0.3},
            {"name": "上传自定义语音", "weight": 0.3},
            {"name": "生成语音模型", "weight": 0.4}
        ]
        progress = MultiStageProgress(progress_stages, "创建自定义语音中...")
        
        # 第一阶段：处理音频片段
        st.info("正在处理选中的音频片段...")
        progress.update_stage(0, 0.5)
        
        try:
            # 读取选中的音频片段数据
            with open(selected_audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            st.info("音频片段处理完成")
            progress.update_stage(0, 1.0)
            
            # 第二阶段：上传自定义语音
            st.info("正在上传自定义语音...")
            progress.update_stage(1, 0.3)
            
            # 获取API密钥
            api_key = get_api_key()
            if not api_key:
                st.error("缺少API密钥。请在.env文件中设置SILICONFLOW_API_KEY环境变量。")
            else:
                # 上传自定义语音
                upload_result = upload_custom_voice(api_key, audio_data, sanitized_name, reading_text)
                
                # 检查是否有错误
                if "error" in upload_result:
                    st.error(f"上传失败: {upload_result['error']}")
                    if 'message' in upload_result:
                        st.text(upload_result['message'])
                else:
                    st.info("自定义语音上传成功")
                    progress.update_stage(1, 1.0)
                    
                    # 第三阶段：等待语音模型生成
                    st.info("正在生成语音模型...")
                    progress.update_stage(2, 0.5)
                    
                    # 提取自定义语音ID和名称
                    custom_voice_id = None
                    if "result" in upload_result and "customName" in upload_result["result"]:
                        custom_voice_name = upload_result["result"]["customName"]
                        # 如果有ID信息，也提取
                        if "id" in upload_result["result"]:
                            custom_voice_id = upload_result["result"]["id"]
                    else:
                        # 如果结果结构不符合预期，使用输入的名称
                        custom_voice_name = sanitized_name
                    
                    # 保存结果到会话状态
                    st.session_state.custom_voice_state["created_voice_id"] = custom_voice_id
                    st.session_state.custom_voice_state["created_voice_name"] = custom_voice_name
                    st.session_state.custom_voice_state["success"] = True
                    st.session_state.custom_voice_state["processing_stage"] = "upload"  # 重置为首页
                    
                    # 完成最后阶段
                    st.info("语音模型生成成功")
                    progress.update_stage(2, 1.0)
                    
                    # 显示成功信息
                    time.sleep(1)  # 等待进度条显示完成
                    st.rerun()  # 重新加载页面显示成功信息
        except Exception as e:
            # 处理异常
            st.error(f"创建自定义语音时出错: {str(e)}")
            st.exception(e)
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
            except Exception as e:
                st.warning(f"清理临时文件时出错: {str(e)}")

