#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - API调用封装模块
此模块负责封装与SiliconFlow API的所有交互
"""

import os
import base64
import json
import requests
from pathlib import Path

# 导入配置
import sys
from pathlib import Path

# 确保可以导入项目模块
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import get_api_key

class SiliconFlowAPI:
    """SiliconFlow API封装类，提供与API交互的所有方法"""
    
    def __init__(self):
        """初始化API客户端"""
        self.api_key = get_api_key()
        if not self.api_key:
            raise ValueError("未找到SiliconFlow API密钥，请在.env文件中设置SILICONFLOW_API_KEY")
        
        # API基础URL
        self.base_url = "https://api.siliconflow.cn/v1"
        
        # 基础请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """测试API连接是否正常"""
        try:
            # 尝试获取语音列表作为连接测试
            response = self.get_voices()
            return True, "API连接正常"
        except Exception as e:
            return False, f"API连接失败: {str(e)}"
    
    def transcribe_audio(self, audio_path):
        """
        转录音频文件
        参数:
            audio_path: 音频文件路径
        返回:
            转录结果字典
        """
        # 确认文件存在
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 构建请求数据
        url = f"{self.base_url}/audio/transcriptions"
        
        # 使用files参数直接上传文件，而非base64编码
        files = {
            "file": (os.path.basename(audio_path), open(audio_path, "rb"))
        }
        
        data = {
            "model": "FunAudioLLM/SenseVoiceSmall"
        }
        
        try:
            # 发送请求，使用files和data参数
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(url, headers=headers, files=files, data=data)
            
            # 检查响应
            if response.status_code == 200:
                return response.json()
            else:
                error_message = f"转录失败: {response.status_code} - {response.text}"
                raise Exception(error_message)
        finally:
            # 确保文件被关闭
            files["file"][1].close()
    
    def get_voices(self):
        """
        获取可用的语音列表
        返回:
            语音列表
        """
        url = f"{self.base_url}/audio/voice/list"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # 解析返回的JSON数据
            data = response.json()
            # API返回的数据结构包含一个"result"字段，里面才是语音列表
            if "result" in data and isinstance(data["result"], list):
                return data
            else:
                print(f"返回的数据结构不符合预期: {data}")
                return {"result": []}
        else:
            error_message = f"获取语音列表失败: {response.status_code} - {response.text}"
            raise Exception(error_message)
    
    def upload_voice(self, audio_path, voice_name, text=None):
        """
        上传自定义语音
        参数:
            audio_path: 音频文件路径
            voice_name: 自定义语音名称
            text: 音频中的朗读文本(可选)
        返回:
            上传结果字典
        """
        # 确认文件存在
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 读取音频文件并转为base64
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()
            audio_base64 = base64.b64encode(audio_content).decode("utf-8")
        
        # 构建请求数据
        url = f"{self.base_url}/uploads/audio/voice"
        data = {
            "customName": voice_name,
            "audio": f'data:audio/mpeg;base64,{audio_base64}',
            "model": "FunAudioLLM/CosyVoice2-0.5B"
        }
        
        # 如果提供了文本，添加到请求中
        if text:
            data["text"] = text
        
        # 发送请求
        response = requests.post(url, headers=self.headers, json=data)
        
        # 检查响应
        if response.status_code == 200:
            return response.json()
        else:
            error_message = f"上传语音失败: {response.status_code} - {response.text}"
            raise Exception(error_message)
    
    def create_speech(self, text, voice, speed=1.0, sample_rate=44100, output_format="mp3", stream=False, model="FunAudioLLM/CosyVoice2-0.5B"):
        """
        生成语音
        参数:
            text: 要转换为语音的文本
            voice: 语音URI或名称
            speed: 语音速度，默认1.0
            sample_rate: 采样率，默认44100
            output_format: 输出格式，默认mp3
            stream: 是否使用流式模式，适合长文本
            model: 语音模型，默认为 CosyVoice2-0.5B
        返回:
            二进制音频数据
        """
        # 构建请求URL和数据
        url = f"{self.base_url}/audio/speech"
        if stream:
            url += "/stream"
        
        # 使用input字段而不是text字段，符合最新API格式
        data = {
            "input": text,  # 关键变化：使用input字段
            "voice": voice,
            "speed": speed,
            "sample_rate": sample_rate,
            "response_format": output_format,  # 关键变化：使用response_format而不是format
            "model": model,
            "stream": stream  # 添加stream参数
        }
        
        # 发送请求
        response = requests.post(url, headers=self.headers, json=data, stream=stream)
        
        # 检查响应
        if response.status_code == 200:
            return response.content
        else:
            error_message = f"生成语音失败: {response.status_code} - {response.text}"
            raise Exception(error_message)
    
    def save_speech_to_file(self, text, voice_uri, output_path, speed=1.0, sample_rate=44100, stream=False, model="FunAudioLLM/CosyVoice2-0.5B"):
        """
        生成语音并保存到文件
        参数:
            text: 要转换为语音的文本
            voice_uri: 语音URI或名称
            output_path: 输出文件路径
            speed: 语音速度，默认1.0
            sample_rate: 采样率，默认44100
            stream: 是否使用流式模式，适合长文本
            model: 语音模型，默认为 CosyVoice2-0.5B
        返回:
            输出文件路径
        """
        # 确定输出格式
        output_format = os.path.splitext(output_path)[1].lstrip(".")
        if not output_format:
            output_format = "mp3"
            output_path += ".mp3"
        
        # 生成语音
        audio_data = self.create_speech(
            text=text,
            voice=voice_uri,
            speed=speed,
            sample_rate=sample_rate,
            output_format=output_format,
            stream=stream,
            model=model
        )
        
        # 保存到文件
        with open(output_path, "wb") as f:
            f.write(audio_data)
        
        return output_path
