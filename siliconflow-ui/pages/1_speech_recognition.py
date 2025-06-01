#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 语音识别页面
提供语音转文本功能，支持单个和批量处理
"""

import os
import streamlit as st
import tempfile
import pandas as pd
import time
import sys
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="语音识别 - SiliconFlow语音工具集",
    page_icon="🎤",
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
from app.components.file_uploader import audio_uploader, multi_audio_uploader
from app.components.audio_player import enhanced_audio_player
from app.components.progress import TranscriptionProgress

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

# 缓存转录结果
@st.cache_data
def transcribe_audio_cached(file_path):
    """缓存音频转录结果，避免重复处理"""
    api = get_api_client()
    return api.transcribe_audio(file_path)

# 主页面内容
st.title("🎤 语音识别")

st.markdown("""
在这里，您可以将音频文件转换为文本。上传音频文件，我们的AI将帮您识别其中的语音内容。

- 支持单个文件处理和批量处理
- 支持多种音频格式（mp3, wav, ogg, flac, m4a）
- 自动保存和导出转录结果
""")

# 创建选项卡
tab1, tab2 = st.tabs(["单个文件", "批量处理"])

# 单个文件处理选项卡
with tab1:
    st.subheader("单个文件转录")
    
    # 上传音频文件
    uploaded_file = audio_uploader("上传音频文件", key="single_audio_upload")
    
    if uploaded_file:
        # 显示音频预览
        st.subheader("音频预览")
        enhanced_audio_player(uploaded_file.getvalue(), key="preview_audio")
        
        # 转录选项
        st.subheader("转录选项")
        col1, col2 = st.columns(2)
        with col1:
            save_output = st.checkbox("保存转录结果", value=True)
        with col2:
            output_format = st.selectbox("输出格式", ["TXT", "JSON"])
        
        # 开始转录按钮
        if st.button("开始转录", type="primary"):
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{uploaded_file.name.split(".")[-1]}', delete=False) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name
            
            try:
                # 显示处理进度
                progress = TranscriptionProgress("转录进度")
                
                # 更新进度
                progress.update(0.3, "正在准备音频...")
                
                # 调用API进行转录
                progress.update(0.5, "正在执行转录...")
                
                # 获取API客户端
                api = get_api_client()
                
                try:
                    # 执行转录
                    result = transcribe_audio_cached(temp_file_path)
                    
                    # 更新进度
                    progress.update(1.0, "转录完成!")
                    
                    # 检查结果
                    if result and 'text' in result:
                        text = result['text']
                        
                        # 保存到状态
                        StateManager.save_stt_result(uploaded_file.name, text)
                        
                        # 显示转录结果
                        st.success("转录成功!")
                        
                        st.subheader("转录结果")
                        st.text_area("文本内容:", value=text, height=200)
                        
                        # 保存结果
                        if save_output:
                            output_filename = f"{uploaded_file.name.split('.')[0]}.{output_format.lower()}"
                            
                            if output_format == "TXT":
                                output_data = text
                                mime_type = "text/plain"
                            else:  # JSON
                                import json
                                output_data = json.dumps(result, ensure_ascii=False, indent=2)
                                mime_type = "application/json"
                            
                            # 下载按钮
                            st.download_button(
                                label=f"下载{output_format}文件",
                                data=output_data,
                                file_name=output_filename,
                                mime=mime_type
                            )
                    else:
                        st.error("转录失败，请检查音频文件和API密钥")
                except Exception as e:
                    st.error(f"转录过程出错: {str(e)}")
                    progress.update(1.0, f"转录出错: {str(e)}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

# 批量处理选项卡
with tab2:
    st.subheader("批量文件转录")
    
    # 批量上传选项
    uploaded_files = multi_audio_uploader("上传多个音频文件", key="batch_audio_upload")
    
    # 批处理选项
    if uploaded_files:
        st.subheader("批处理选项")
        
        col1, col2 = st.columns(2)
        with col1:
            save_individual = st.checkbox("单独保存每个转录结果", value=True)
        with col2:
            save_combined = st.checkbox("合并保存所有结果", value=True)
        
        # 开始批量处理
        if st.button("开始批量转录", type="primary"):
            results = []
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 初始化进度显示
                progress = TranscriptionProgress()
                progress.start_batch(len(uploaded_files))
                
                # 保存上传的文件到临时目录
                file_paths = []
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)
                
                # 获取API客户端
                api = get_api_client()
                
                # 处理每个文件
                for i, file_path in enumerate(file_paths):
                    file_name = os.path.basename(file_path)
                    
                    try:
                        # 调用API进行转录
                        result = api.transcribe_audio(file_path)
                        
                        if result and 'text' in result:
                            text = result['text']
                            
                            # 保存结果
                            file_result = {
                                "文件名": file_name,
                                "转录文本": text,
                                "状态": "成功"
                            }
                            
                            # 单独保存
                            if save_individual:
                                output_file = os.path.splitext(file_name)[0] + '.txt'
                                output_path = os.path.join(temp_dir, output_file)
                                with open(output_path, 'w', encoding='utf-8') as f:
                                    f.write(text)
                            
                            # 标记成功
                            progress.file_complete(file_name, True)
                        else:
                            file_result = {
                                "文件名": file_name,
                                "转录文本": "",
                                "状态": "失败"
                            }
                            
                            # 标记失败
                            progress.file_complete(file_name, False)
                    except Exception as e:
                        file_result = {
                            "文件名": file_name,
                            "转录文本": "",
                            "状态": f"错误: {str(e)}"
                        }
                        
                        # 标记失败
                        progress.file_complete(file_name, False)
                    
                    # 添加到结果列表
                    results.append(file_result)
                
                # 显示处理统计
                success_count = sum(1 for r in results if r["状态"] == "成功")
                
                # 显示结果表格
                if results:
                    st.subheader("转录结果")
                    
                    # 创建数据框
                    df = pd.DataFrame(results)
                    
                    # 使用数据编辑器显示结果
                    st.data_editor(
                        df,
                        column_config={
                            "文件名": st.column_config.TextColumn("文件名"),
                            "转录文本": st.column_config.TextColumn("转录文本", width="large"),
                            "状态": st.column_config.TextColumn("状态", width="small")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # 合并保存所有结果
                    if save_combined:
                        st.subheader("下载结果")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # CSV格式
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="下载CSV汇总",
                                data=csv,
                                file_name="转录结果汇总.csv",
                                mime="text/csv"
                            )
                        
                        with col2:
                            # 文本格式 - 每个文件一段
                            text_content = ""
                            for r in results:
                                if r["状态"] == "成功":
                                    text_content += f"=== {r['文件名']} ===\n{r['转录文本']}\n\n"
                            
                            st.download_button(
                                label="下载TXT汇总",
                                data=text_content,
                                file_name="转录结果汇总.txt",
                                mime="text/plain"
                            )
