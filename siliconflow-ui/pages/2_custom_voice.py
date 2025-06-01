#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 自定义语音页面
允许用户上传音频样本创建个性化语音模型
"""

import os
import streamlit as st
import tempfile
import time
import pandas as pd
import sys
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="自定义语音 - SiliconFlow语音工具集",
    page_icon="🗣️",
    layout="wide"
)

# 确保可以导入项目模块
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "app"))

# 导入工具模块
from app.utils.state import StateManager
from app.utils.api import SiliconFlowAPI
from app.config import get_api_key, AUDIO_DIR
from app.components.file_uploader import audio_uploader, multi_audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import VoiceUploadProgress

# 加载自定义CSS样式 - 苹果设计风格
def load_css_file(css_file_path):
    with open(css_file_path, 'r') as f:
        return f.read()

# 尝试加载自定义CSS文件，如果存在的话
custom_css_path = ROOT_DIR / ".streamlit" / "style.css"
if custom_css_path.exists():
    custom_css = load_css_file(custom_css_path)
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# 初始化会话状态
StateManager.initialize_session_state()

# 初始化API连接
@st.cache_resource(show_spinner="正在连接SiliconFlow API...")
def init_api():
    """初始化API连接，使用缓存避免重复初始化"""
    try:
        api = SiliconFlowAPI()
        # 尝试连接API
        connected, message = api.test_connection()
        
        # 更新API状态
        StateManager.set_api_status(connected, message)
        
        # 如果连接成功，获取并缓存语音列表
        if connected:
            try:
                # 主动获取语音列表
                voices = api.get_voices()
                StateManager.update_voices_list(voices)
            except Exception as e:
                st.warning(f"获取语音列表失败: {str(e)}")
        else:
            st.error(f"API连接失败: {message}")
            
        return api
    except Exception as e:
        error_msg = f"API初始化失败: {str(e)}"
        StateManager.set_api_status(False, error_msg)
        st.error(error_msg)
        return None

# 在页面加载时初始化API
api = init_api()

# 在侧边栏显示API状态信息
with st.sidebar:
    st.title("SiliconFlow语音工具集")
    
    # 检查API状态
    api_key = get_api_key()
    api_status = StateManager.get_api_status()
    
    if api_key:
        # 显示API状态
        if api_status["connected"]:
            st.success("✅ API连接正常")
        else:
            st.error(f"❌ API连接失败: {api_status['message']}")
    else:
        st.error("❌ 未找到API密钥")
        st.info("请返回首页设置API密钥")

# 缓存API客户端
@st.cache_resource
def get_api_client():
    """获取API客户端实例"""
    return SiliconFlowAPI()

# 主页面内容
st.title("🗣️ 自定义语音")

st.markdown("""
在这里，您可以上传自己的声音样本，创建个性化语音模型。上传的样本越多，生成的语音效果越好。

- 支持单个或批量上传音频样本
- 提供样本质量检查和建议
- 可以试听生成的语音效果
- 可管理已创建的自定义语音
""")

# 创建选项卡
tab1, tab2 = st.tabs(["创建自定义语音", "管理我的语音"])

# 创建自定义语音选项卡
with tab1:
    st.subheader("创建自定义语音")
    
    # 表单输入基本信息
    with st.form("voice_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            voice_name = st.text_input(
                "语音名称",
                placeholder="为您的语音起个名字，如小明的声音",
                help="名称将显示在语音列表中，便于识别"
            )
        
        with col2:
            # 创建可选的语音描述
            voice_description = st.text_input(
                "语音描述（可选）",
                placeholder="描述这个语音的特点，如男声，温柔",
                help="描述有助于更好地区分不同语音"
            )
        
        # 性别选择
        gender = st.radio(
            "语音性别",
            options=["男", "女", "其他"],
            horizontal=True,
            help="选择与音频样本相符的性别"
        )
        
        # 提交按钮
        submit_form = st.form_submit_button("下一步: 上传音频样本")
    
    # 如果表单已提交，继续上传音频
    if submit_form or st.session_state.voice_state.get("form_submitted", False):
        # 标记表单已提交
        st.session_state.voice_state["form_submitted"] = True
        
        # 保存表单数据
        st.session_state.voice_state["voice_name"] = voice_name if submit_form else st.session_state.voice_state.get("voice_name", "")
        st.session_state.voice_state["voice_description"] = voice_description if submit_form else st.session_state.voice_state.get("voice_description", "")
        st.session_state.voice_state["gender"] = gender if submit_form else st.session_state.voice_state.get("gender", "男")
        
        # 验证表单数据
        if not st.session_state.voice_state["voice_name"]:
            st.error("请输入语音名称")
        else:
            # 显示上传音频区域
            st.subheader("上传音频样本")
            
            st.markdown("""
            #### 音频样本要求
            - 格式: MP3, WAV, FLAC (推荐WAV格式, 44.1kHz采样率)
            - 时长: 每个样本5秒至10分钟
            - 数量: 最少5个样本，建议10-20个效果更佳
            - 质量: 清晰无噪音，尽量使用相同设备录制
            """)
            
            # 选择上传方式
            upload_method = st.radio(
                "选择上传方式",
                options=["批量上传", "单个上传"],
                horizontal=True,
                help="批量上传更快，单个上传可预览"
            )
            
            if upload_method == "批量上传":
                # 批量上传音频文件
                uploaded_files = multi_audio_uploader(
                    "选择多个音频文件",
                    key="voice_batch_upload",
                    help="同时选择多个音频文件上传"
                )
                
                if uploaded_files:
                    # 显示已上传的文件列表
                    st.write(f"已选择 {len(uploaded_files)} 个文件")
                    
                    # 创建开始上传按钮
                    if st.button("开始上传", type="primary"):
                        # 获取API客户端
                        api = get_api_client()
                        
                        # 创建临时目录
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 初始化进度显示
                            progress = VoiceUploadProgress()
                            progress.start_batch(len(uploaded_files))
                            
                            # 保存上传的文件到临时目录
                            file_paths = []
                            for uploaded_file in uploaded_files:
                                file_path = os.path.join(temp_dir, uploaded_file.name)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                file_paths.append((file_path, uploaded_file.name))
                            
                            # 上传音频样本创建自定义语音
                            try:
                                # 转换性别格式
                                gender_map = {"男": "male", "女": "female", "其他": "other"}
                                gender_code = gender_map.get(st.session_state.voice_state["gender"], "other")
                                
                                # 创建语音
                                result = api.create_voice(
                                    name=st.session_state.voice_state["voice_name"],
                                    description=st.session_state.voice_state["voice_description"] or None,
                                    gender=gender_code,
                                    audio_files=file_paths,
                                    progress_callback=progress.update_file_progress
                                )
                                
                                if result and "voice" in result:
                                    # 保存语音信息
                                    voice_info = result["voice"]
                                    
                                    # 显示成功信息
                                    st.success(f"自定义语音创建成功! 语音ID: {voice_info.get('id', '未知')}")
                                    
                                    # 显示创建的语音信息
                                    st.json(voice_info)
                                    
                                    # 刷新语音列表
                                    StateManager.reset_voices_cache()
                                    voices_list = api.get_voices()
                                    StateManager.update_voices_list(voices_list)
                                    
                                    # 提供测试按钮
                                    if st.button("测试生成的语音"):
                                        # 在多页面应用结构中使用URL导航而非state
                                        st.switch_page("3_text_to_speech.py")
                                else:
                                    st.error("创建语音失败，请检查音频样本和API连接")
                            except Exception as e:
                                st.error(f"创建语音过程出错: {str(e)}")
            else:
                # 单个上传
                uploaded_file = audio_uploader(
                    "选择一个音频文件",
                    key="voice_single_upload",
                    help="选择一个音频文件上传并预览"
                )
                
                if uploaded_file:
                    # 显示音频预览
                    st.subheader("音频预览")
                    enhanced_audio_player(uploaded_file.getvalue(), key="preview_voice_audio")
                    
                    # 添加到待上传列表
                    if "upload_queue" not in st.session_state.voice_state:
                        st.session_state.voice_state["upload_queue"] = []
                    
                    # 检查是否已经在队列中
                    file_names = [f[1] for f in st.session_state.voice_state["upload_queue"]]
                    
                    if uploaded_file.name not in file_names and st.button("添加到上传队列"):
                        # 保存到临时文件
                        with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                            temp_file.write(uploaded_file.getbuffer())
                            temp_file_path = temp_file.name
                        
                        # 添加到队列
                        st.session_state.voice_state["upload_queue"].append((temp_file_path, uploaded_file.name))
                        st.success(f"已添加到上传队列: {uploaded_file.name}")
                        st.rerun()
                
                # 显示上传队列
                if "upload_queue" in st.session_state.voice_state and st.session_state.voice_state["upload_queue"]:
                    st.subheader("上传队列")
                    
                    # 显示队列中的文件
                    for i, (_, file_name) in enumerate(st.session_state.voice_state["upload_queue"]):
                        st.write(f"{i+1}. {file_name}")
                    
                    # 显示队列操作按钮
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("清空队列"):
                            # 清除临时文件
                            for temp_path, _ in st.session_state.voice_state["upload_queue"]:
                                if os.path.exists(temp_path):
                                    os.unlink(temp_path)
                            
                            # 清空队列
                            st.session_state.voice_state["upload_queue"] = []
                            st.success("已清空上传队列")
                            st.rerun()
                    
                    with col2:
                        if len(st.session_state.voice_state["upload_queue"]) >= 5:
                            if st.button("开始上传", type="primary"):
                                # 获取API客户端
                                api = get_api_client()
                                
                                # 初始化进度显示
                                progress = VoiceUploadProgress()
                                progress.start_batch(len(st.session_state.voice_state["upload_queue"]))
                                
                                # 上传音频样本创建自定义语音
                                try:
                                    # 转换性别格式
                                    gender_map = {"男": "male", "女": "female", "其他": "other"}
                                    gender_code = gender_map.get(st.session_state.voice_state["gender"], "other")
                                    
                                    # 创建语音
                                    result = api.create_voice(
                                        name=st.session_state.voice_state["voice_name"],
                                        description=st.session_state.voice_state["voice_description"] or None,
                                        gender=gender_code,
                                        audio_files=st.session_state.voice_state["upload_queue"],
                                        progress_callback=progress.update_file_progress
                                    )
                                    
                                    if result and "voice" in result:
                                        # 保存语音信息
                                        voice_info = result["voice"]
                                        
                                        # 显示成功信息
                                        st.success(f"自定义语音创建成功! 语音ID: {voice_info.get('id', '未知')}")
                                        
                                        # 显示创建的语音信息
                                        st.json(voice_info)
                                        
                                        # 刷新语音列表
                                        StateManager.reset_voices_cache()
                                        voices_list = api.get_voices()
                                        StateManager.update_voices_list(voices_list)
                                        
                                        # 清除临时文件
                                        for temp_path, _ in st.session_state.voice_state["upload_queue"]:
                                            if os.path.exists(temp_path):
                                                os.unlink(temp_path)
                                        
                                        # 清空队列
                                        st.session_state.voice_state["upload_queue"] = []
                                        
                                        # 提供测试按钮
                                        if st.button("测试生成的语音"):
                                            # 在多页面应用结构中使用URL导航而非state
                                            st.switch_page("3_text_to_speech.py")
                                    else:
                                        st.error("创建语音失败，请检查音频样本和API连接")
                                except Exception as e:
                                    st.error(f"创建语音过程出错: {str(e)}")
                        else:
                            st.warning("至少需要5个音频样本才能创建语音")

    # 使用建议
    with st.expander("录制样本建议", expanded=False):
        st.markdown("""
        ### 录制高质量音频样本的建议
        
        1. **环境要求**
           - 选择安静的环境，避免背景噪音
           - 关闭空调、风扇等会产生持续噪音的设备
           - 避免混响严重的大房间
        
        2. **设备选择**
           - 使用好的麦克风，可以是手机或电脑的内置麦克风
           - 保持固定的录音距离，通常10-20厘米较佳
           - 避免触碰麦克风或震动设备
        
        3. **录制内容**
           - 使用自然的语速和语调朗读文本
           - 避免过度情感化的表达，保持平稳
           - 内容应当多样化，包含不同类型的句子
           - 建议使用中文和英文混合的内容
        
        4. **录制技巧**
           - 每段录音开始前留0.5-1秒空白
           - 每段录音结束后留0.5-1秒空白
           - 出现口误时重新录制该片段
           - 保持一致的音量和语速
        """)

# 管理我的语音选项卡
with tab2:
    st.subheader("管理我的语音")
    
    # 获取API客户端
    api = get_api_client()
    
    # 刷新按钮
    if st.button("刷新语音列表"):
        StateManager.reset_voices_cache()
        with st.spinner("正在刷新语音列表..."):
            try:
                voices_list = api.get_voices()
                StateManager.update_voices_list(voices_list)
                st.success("语音列表已刷新")
            except Exception as e:
                st.error(f"刷新语音列表失败: {str(e)}")
    
    # 获取语音列表
    voices_list = StateManager.get_voices_list()
    
    if not voices_list or "result" not in voices_list:
        st.warning("未能获取语音列表，请检查API连接")
    else:
        # 从 result 字段中获取语音列表
        # 在此处我们假设所有语音都是自定义语音，因为API结构发生了变化
        custom_voices = voices_list["result"]
        
        if not custom_voices:
            st.info("您还没有创建自定义语音，请前往'创建自定义语音'选项卡创建")
        else:
            # 创建语音列表数据
            voice_data = []
            for voice in custom_voices:
                # 使用新的API返回数据结构中的字段
                model = voice.get("model", "未知")  # 添加模型字段
                voice_data.append({
                    "ID": voice.get("uri", "未知"),  # 使用uri作为ID
                    "名称": voice.get("customName", "未知"),  # 使用customName作为名称
                    "描述": model,  # 将模型名称作为描述
                    "样本文本": voice.get("text", "")[:30] + "..." if len(voice.get("text", "")) > 30 else voice.get("text", "")
                })
            
            # 创建数据框
            df = pd.DataFrame(voice_data)
            
            # 显示语音列表
            st.dataframe(
                df,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "名称": st.column_config.TextColumn("名称", width="medium"),
                    "描述": st.column_config.TextColumn("模型", width="medium"),
                    "样本文本": st.column_config.TextColumn("样本文本", width="large")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # 选择要管理的语音
            selected_voice_id = st.selectbox(
                "选择要管理的语音",
                options=[v["ID"] for v in voice_data],
                format_func=lambda x: next((v["名称"] for v in voice_data if v["ID"] == x), x)
            )
            
            if selected_voice_id:
                # 获取选中的语音详情
                selected_voice = next((v for v in custom_voices if v.get("uri") == selected_voice_id), None)
                
                if selected_voice:
                    st.subheader(f"语音详情: {selected_voice.get('customName', '未知')}")
                    
                    # 显示语音信息
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"ID: {selected_voice.get('uri', '未知')}")
                        st.write(f"名称: {selected_voice.get('customName', '未知')}")
                        st.write(f"模型: {selected_voice.get('model', '未知')}")
                    
                    with col2:
                        # 显示样本文本
                        sample_text = selected_voice.get('text', '')
                        st.write(f"样本文本: {sample_text[:100]}{'...' if len(sample_text) > 100 else ''}")
                    
                    # 操作按钮
                    st.subheader("操作")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("使用此语音生成语音"):
                            # 设置为当前选中的语音
                            st.session_state.tts_state["selected_voice"] = selected_voice_id
                            # 跳转到TTS页面
                            st.switch_page("3_text_to_speech.py")
                    
                    with col2:
                        # 删除语音按钮 (当前版本的API可能不支持删除操作)
                        if st.button("删除此语音", type="secondary", disabled=True):
                            st.warning("当前版本不支持删除语音操作")
                    
                    # 测试语音
                    st.subheader("测试语音")
                    
                    test_text = st.text_area(
                        "输入测试文本",
                        value="这是一段测试文本，用于测试自定义语音的效果。",
                        height=100
                    )
                    
                    if st.button("生成测试音频"):
                        if test_text:
                            try:
                                # 显示处理进度
                                with st.spinner("正在生成测试音频..."):
                                    # 生成测试音频
                                    audio_bytes = api.create_speech(
                                        text=test_text,
                                        voice=selected_voice_id,
                                        model="FunAudioLLM/CosyVoice2-0.5B"  # 使用默认模型
                                    )
                                
                                # 显示音频播放器
                                if audio_bytes:
                                    st.success("测试音频生成成功")
                                    st.audio(audio_bytes, format="audio/mp3")
                                    
                                    # 保存按钮
                                    st.download_button(
                                        label="下载测试音频",
                                        data=audio_bytes,
                                        file_name=f"test_{selected_voice.get('customName', 'voice')}.mp3",
                                        mime="audio/mp3"
                                    )
                                else:
                                    st.error("生成测试音频失败")
                            except Exception as e:
                                st.error(f"生成音频时出错: {str(e)}")
                        else:
                            st.warning("请输入测试文本")
