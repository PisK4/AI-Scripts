#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 状态管理模块
此模块负责管理应用程序的状态，实现跨页面数据共享
"""

import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

class StateManager:
    """状态管理类，负责管理应用程序中的各种状态"""
    
    @staticmethod
    def initialize_session_state():
        """初始化会话状态"""
        # 初始化基本导航状态
        if "page" not in st.session_state:
            st.session_state.page = "home"
        
        # 初始化API状态
        if "api_status" not in st.session_state:
            st.session_state.api_status = {
                "connected": False,
                "message": "未连接到API"
            }
        
        # 初始化语音识别状态
        if "stt_state" not in st.session_state:
            st.session_state.stt_state = {
                "uploaded_files": [],
                "processing_results": [],
                "current_tab": "单个文件"
            }
        
        # 初始化文本转语音状态
        if "tts_state" not in st.session_state:
            st.session_state.tts_state = {
                "selected_voice": None,
                "text_input": "",
                "speed": 1.0,
                "sample_rate": 24000,
                "generated_audio": None
            }
        
        # 初始化自定义语音状态
        if "voice_state" not in st.session_state:
            st.session_state.voice_state = {
                "uploaded_audio": None,
                "voice_name": "",
                "read_text": "",
                "created_voice_uri": None
            }
        
        # 初始化一体化处理状态
        if "integrated_state" not in st.session_state:
            st.session_state.integrated_state = {
                "input_files": [],
                "stage": "upload",  # upload, process, results
                "results": []
            }
        
        # 初始化语音列表
        if "voices_list" not in st.session_state:
            st.session_state.voices_list = []
    
    @staticmethod
    def set_page(page_name):
        """设置当前页面"""
        st.session_state.page = page_name
    
    @staticmethod
    def get_current_page():
        """获取当前页面"""
        return st.session_state.page
    
    @staticmethod
    def set_api_status(connected, message):
        """设置API连接状态"""
        st.session_state.api_status = {
            "connected": connected,
            "message": message
        }
    
    @staticmethod
    def get_api_status():
        """获取API连接状态"""
        return st.session_state.api_status
    
    @staticmethod
    def update_voices_list(voices_list):
        """更新语音列表"""
        st.session_state.voices_list = voices_list
    
    @staticmethod
    def get_voices_list():
        """获取语音列表"""
        return st.session_state.voices_list
    
    @staticmethod
    def reset_state(state_name):
        """重置特定状态"""
        if state_name == "stt_state":
            st.session_state.stt_state = {
                "uploaded_files": [],
                "processing_results": [],
                "current_tab": "单个文件"
            }
        elif state_name == "tts_state":
            st.session_state.tts_state = {
                "selected_voice": None,
                "text_input": "",
                "speed": 1.0,
                "sample_rate": 24000,
                "generated_audio": None
            }
        elif state_name == "voice_state":
            st.session_state.voice_state = {
                "uploaded_audio": None,
                "voice_name": "",
                "read_text": "",
                "created_voice_uri": None
            }
        elif state_name == "integrated_state":
            st.session_state.integrated_state = {
                "input_files": [],
                "stage": "upload",
                "results": []
            }
    
    @staticmethod
    def save_stt_result(file_name, text, status="成功"):
        """保存语音识别结果"""
        result = {
            "文件名": file_name,
            "转录文本": text,
            "状态": status
        }
        
        st.session_state.stt_state["processing_results"].append(result)
    
    @staticmethod
    def get_stt_results():
        """获取语音识别结果"""
        return st.session_state.stt_state["processing_results"]
