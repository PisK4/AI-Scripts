#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSS样式模块
提供UI界面样式定义
"""

import streamlit as st

def apple_css():
    """应用Apple风格的CSS样式"""
    
    # 定义Apple风格CSS
    st.markdown("""
    <style>
    /* 主字体和基本样式 */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #2d2d2d;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.2rem;
        letter-spacing: -0.01em;
    }
    
    h2 {
        font-size: 1.8rem;
        letter-spacing: -0.01em;
        margin-top: 1.5rem;
    }
    
    h3 {
        font-size: 1.3rem;
        letter-spacing: -0.01em;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 8px;
        padding: 0.3rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* 选择器样式 */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* 滑块样式 */
    .stSlider > div > div {
        padding-top: 0.5rem;
    }
    
    /* 分割线样式 */
    .stDivider {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* 卡片样式 */
    .css-1r6slb0, .css-12oz5g7 {
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 信息框样式 */
    .stAlert {
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div {
        border-radius: 10px;
        height: 0.5rem;
    }
    
    /* 自定义文本样式 */
    .caption {
        font-size: 0.9rem;
        color: #6c6c6c;
    }
    
    .small-text {
        font-size: 0.85rem;
    }
    
    .text-center {
        text-align: center;
    }
    
    /* 下载按钮样式 */
    .stDownloadButton > button {
        border-radius: 8px;
        padding: 0.3rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* 文件上传区域样式 */
    .uploadedFile {
        border-radius: 8px;
        border: 1px dashed #d0d0d0;
        padding: 1rem;
    }
    
    /* 音频播放器样式 */
    audio {
        width: 100%;
        border-radius: 30px;
        margin: 0.5rem 0;
    }
    
    /* 选项卡样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* 表格样式 */
    .stTable, .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stTable thead tr th, .stDataFrame thead tr th {
        background-color: #f9f9f9;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def dark_mode_css():
    """应用深色模式的CSS样式"""
    
    st.markdown("""
    <style>
    /* 深色模式基本样式 */
    body {
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    
    /* 深色模式标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    
    /* 深色模式卡片样式 */
    .css-1r6slb0, .css-12oz5g7 {
        background: #262626;
        border: 1px solid #333333;
    }
    
    /* 深色模式输入框样式 */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input {
        background: #333333;
        color: #f0f0f0;
        border: 1px solid #444444;
    }
    
    /* 深色模式选择器样式 */
    .stSelectbox > div > div {
        background: #333333;
        color: #f0f0f0;
        border: 1px solid #444444;
    }
    
    /* 深色模式表格样式 */
    .stTable thead tr th, .stDataFrame thead tr th {
        background-color: #333333;
        color: #ffffff;
    }
    
    .stTable tbody tr, .stDataFrame tbody tr {
        background-color: #262626;
    }
    </style>
    """, unsafe_allow_html=True)
