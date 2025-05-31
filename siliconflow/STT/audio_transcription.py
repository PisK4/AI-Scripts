#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音转文本工具

这个脚本可以将音频文件转换为文本，使用 SiliconFlow API 实现语音识别功能。
使用方法：
    python audio_transcription.py <音频文件路径>
    python audio_transcription.py --dir <目录路径>

注意：需要在.env文件中配置SILICONFLOW_API_KEY
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv


# 加载.env文件中的环境变量
def load_api_key():
    """
    从.env文件加载API密钥
    
    返回:
        str: API密钥
    """
    # 获取siliconflow目录的.env文件路径
    dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    # 从环境变量获取API密钥
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("错误: SILICONFLOW_API_KEY环境变量未设置，请在.env文件中配置")
        return None
    
    return api_key


def transcribe_audio(audio_file_path, token=None):
    """
    将音频文件转换为文本
    
    参数:
        audio_file_path (str): 音频文件的路径
        token (str, 可选): API令牌，如果不提供，将从.env文件获取
        
    返回:
        dict: API 返回的结果
    """
    # 检查文件是否存在
    if not os.path.exists(audio_file_path):
        print(f"错误: 文件 '{audio_file_path}' 不存在")
        return None
    
    # 获取 API 令牌
    if token is None:
        token = load_api_key()
        if token is None:
            return None
    
    # API 端点
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备文件和模型数据
    files = {
        "file": (os.path.basename(audio_file_path), open(audio_file_path, "rb"))
    }
    data = {
        "model": "FunAudioLLM/SenseVoiceSmall"
    }
    
    print(f"正在处理音频文件: {os.path.basename(audio_file_path)}")
    
    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, files=files, data=data)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print("转换成功!")
            return result
        else:
            print(f"错误: API 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return None
    finally:
        # 确保文件被关闭
        files["file"][1].close()


def process_directory(directory_path, token=None, output_dir=None):
    """
    处理目录中的所有音频文件
    
    参数:
        directory_path (str): 音频文件目录的路径
        token (str, 可选): API令牌
        output_dir (str, 可选): 输出目录，默认与输入目录相同
    """
    # 如果没有指定输出目录，使用输入目录
    if output_dir is None:
        output_dir = directory_path
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历目录中的所有文件
    audio_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        
        # 检查文件是否是音频文件
        file_ext = os.path.splitext(file_name)[1].lower()
        if os.path.isfile(file_path) and file_ext in audio_extensions:
            # 处理音频文件
            result = transcribe_audio(file_path, token)
            
            if result:
                # 获取转录文本
                transcription = result.get('text', '')
                
                # 创建输出文件名（使用与音频文件相同的名称，但扩展名为.txt）
                output_file_name = os.path.splitext(file_name)[0] + '.txt'
                output_file_path = os.path.join(output_dir, output_file_name)
                
                # 保存转录文本到文件
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                
                print(f"已保存转录结果到: {output_file_path}")


def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  处理单个文件: python audio_transcription.py <音频文件路径>")
        print("  处理整个目录: python audio_transcription.py --dir <目录路径>")
        return
    
    # 预先加载API密钥
    token = load_api_key()
    if token is None:
        return
    
    # 处理命令行参数
    if sys.argv[1] == "--dir":
        if len(sys.argv) < 3:
            print("错误: 使用 --dir 选项时必须提供目录路径")
            return
        
        directory_path = sys.argv[2]
        process_directory(directory_path, token)
    else:
        audio_file_path = sys.argv[1]
        result = transcribe_audio(audio_file_path, token)
        if result:
            print("转录结果:")
            print(result.get('text', ''))


if __name__ == "__main__":
    main()
