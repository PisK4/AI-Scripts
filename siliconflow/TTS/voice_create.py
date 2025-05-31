#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow TTS 语音生成工具
使用SiliconFlow API将文本转换为语音并保存为音频文件
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv


def generate_speech(text, voice_uri, output_file, model="FunAudioLLM/CosyVoice2-0.5B", 
                    response_format="mp3", sample_rate=32000, speed=1.0, gain=0):
    """
    使用SiliconFlow API生成语音并保存到文件
    
    参数:
        text (str): 要转换为语音的文本
        voice_uri (str): 语音URI，如 'speech:2B:ag5cthth2f:kvfcdsgyrbcyruvitvvp'
        output_file (str): 输出文件路径
        model (str): 使用的模型名称
        response_format (str): 输出音频格式，默认为mp3
        sample_rate (int): 采样率，默认为32000
        speed (float): 语速，默认为1.0
        gain (int): 增益，默认为0
    
    返回:
        bool: 成功返回True，失败返回False
    """
    # 加载API密钥
    load_dotenv()
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("错误: 未找到SILICONFLOW_API_KEY环境变量。请在.env文件中设置。")
        return False
    
    # 准备请求数据
    url = "https://api.siliconflow.cn/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 将文本中的空格替换为%20，保持与shell脚本一致
    text = text.replace(' ', '%20')
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice_uri,
        "response_format": response_format,
        "sample_rate": sample_rate,
        "stream": False,  # 设置为False获取完整响应
        "speed": speed,
        "gain": gain
    }
    
    print(f"正在生成语音: '{text}'")
    print(f"使用语音: {voice_uri}")
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            # 保存音频文件
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"语音生成成功，已保存到: {output_file}")
            return True
        else:
            try:
                error_details = response.json()
                print(f"错误: API请求失败 (状态码: {response.status_code})")
                print(f"错误详情: {json.dumps(error_details, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误: API请求失败 (状态码: {response.status_code})")
                print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"错误: 请求过程中发生异常: {str(e)}")
        return False


def list_voices():
    """获取并显示可用的语音列表"""
    voices_file = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "voices.json"
    
    if not voices_file.exists():
        print(f"错误: 未找到语音列表文件 {voices_file}")
        print("请先运行 voice_fetch.py 获取语音列表")
        return []
    
    try:
        with open(voices_file, "r", encoding="utf-8") as f:
            voices = json.load(f)
        
        print("可用语音列表:")
        for i, voice in enumerate(voices, 1):
            print(f"{i}. 名称: {voice.get('name', '未知')}")
            print(f"   URI: {voice.get('uri', '未知')}")
            print(f"   描述: {voice.get('description', '无描述')}")
            print()
        
        return voices
    except Exception as e:
        print(f"错误: 读取语音列表文件时发生异常: {str(e)}")
        return []


def main():
    parser = argparse.ArgumentParser(description="SiliconFlow TTS 语音生成工具")
    
    # 添加参数
    parser.add_argument("text", nargs="?", help="要转换为语音的文本")
    parser.add_argument("-v", "--voice", help="语音URI或语音名称")
    parser.add_argument("-o", "--output", help="输出文件路径 (默认: output.mp3)")
    parser.add_argument("-m", "--model", default="FunAudioLLM/CosyVoice2-0.5B", 
                        help="使用的模型名称 (默认: FunAudioLLM/CosyVoice2-0.5B)")
    parser.add_argument("-f", "--format", default="mp3", choices=["mp3", "wav"], 
                        help="输出音频格式 (默认: mp3)")
    parser.add_argument("-r", "--rate", type=int, default=32000, 
                        help="采样率 (默认: 32000)")
    parser.add_argument("-s", "--speed", type=float, default=1.0, 
                        help="语速 (默认: 1.0)")
    parser.add_argument("-g", "--gain", type=int, default=0, 
                        help="增益 (默认: 0)")
    parser.add_argument("-l", "--list", action="store_true", 
                        help="列出可用的语音")
    
    args = parser.parse_args()
    
    # 如果请求列出语音列表
    if args.list:
        list_voices()
        return
    
    # 检查必要参数
    if not args.text:
        parser.print_help()
        print("\n错误: 必须提供要转换的文本")
        return
    
    if not args.voice:
        parser.print_help()
        print("\n错误: 必须提供语音URI或语音名称 (-v 或 --voice)")
        return
    
    # 设置默认输出文件
    output_file = args.output if args.output else f"output.{args.format}"
    
    # 如果提供的不是URI而是语音名称，尝试从voices.json查找
    voice_uri = args.voice
    if not voice_uri.startswith("speech:"):
        voices = list_voices()
        found = False
        for voice in voices:
            if voice.get("name") == args.voice:
                voice_uri = voice.get("uri")
                found = True
                break
        
        if not found:
            print(f"错误: 未找到名为 '{args.voice}' 的语音")
            print("请使用 -l 或 --list 选项查看可用的语音")
            return
    
    # 生成语音
    generate_speech(
        args.text, 
        voice_uri, 
        output_file,
        model=args.model,
        response_format=args.format,
        sample_rate=args.rate,
        speed=args.speed,
        gain=args.gain
    )


if __name__ == "__main__":
    main()
