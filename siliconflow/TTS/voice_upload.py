#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音上传工具 - 将音频文件上传到SiliconFlow API创建自定义语音
用法: python voice_upload.py <音频文件路径> <自定义语音名称> [<朗读文本>]
"""

import os
import sys
import json
import re
import requests
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# 导入音频处理库
try:
    from pydub import AudioSegment
except ImportError:
    print("正在安装音频处理库pydub...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pydub"])
    from pydub import AudioSegment

def main():
    # 加载.env文件中的环境变量
    dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
    load_dotenv(dotenv_path=dotenv_path)

    # 从环境变量获取API密钥
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("错误: SILICONFLOW_API_KEY环境变量未设置，请在.env文件中配置")
        sys.exit(1)

    # 检查命令行参数
    if len(sys.argv) < 3:
        print(f"用法: {sys.argv[0]} <音频文件路径> <自定义语音名称> [<朗读文本>]")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    # 获取并处理自定义名称，确保符合API要求
    custom_name_raw = sys.argv[2]
    # 处理自定义名称，只保留字母、数字、下划线和连字符
    import re
    custom_name = re.sub(r'[^a-zA-Z0-9_-]', '_', custom_name_raw)
    # 确保名称不超过64个字符
    custom_name = custom_name[:64]
    
    if custom_name != custom_name_raw:
        print(f"注意: 原始名称 '{custom_name_raw}' 已经转换为合法格式: '{custom_name}'")
    
    # 朗读文本是可选的
    text = ""
    if len(sys.argv) >= 4:
        text = sys.argv[3]
    else:
        text = "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始"

    # 检查文件是否存在
    if not os.path.isfile(audio_file_path):
        print(f"错误: 文件 '{audio_file_path}' 不存在")
        sys.exit(1)

    # 获取siliconflow目录路径
    siliconflow_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 打印上传信息
    print(f"正在上传音频文件: {audio_file_path}")
    print(f"自定义语音名称: {custom_name}")
    print(f"朗读文本: {text}")

    # 准备上传数据
    url = "https://api.siliconflow.cn/v1/uploads/audio/voice"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # 准备表单数据
    # 处理音频文件，截取前10秒
    print(f"正在处理音频文件: {audio_file_path}")
    
    # 加载音频文件
    audio = AudioSegment.from_file(audio_file_path)
    
    # 截取前10秒
    duration_ms = min(10000, len(audio))  # 如果音频小于10秒，使用原始长度
    audio_trimmed = audio[:duration_ms]
    
    # 创建临时文件保存截取后的音频
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
        temp_audio_path = temp_file.name
    
    # 调整比特率并导出为高质量MP3
    audio_trimmed.export(temp_audio_path, format="mp3", bitrate="128k")
    print(f"已截取音频到{duration_ms/1000}秒，保存为临时文件")
    
    # 读取处理后的音频文件
    with open(temp_audio_path, 'rb') as f:
        audio_data = f.read()
    
    # 清理临时文件
    os.unlink(temp_audio_path)
    
    # 将音频数据转换为Base64编码，与Shell脚本一致
    import base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    audio_data_uri = f'data:audio/mpeg;base64,{audio_base64}'
    
    # 与Shell脚本保持一致，使用form提交表单数据
    data = {
        'audio': audio_data_uri,
        'customName': custom_name,
        'text': text,
        'model': 'FunAudioLLM/CosyVoice2-0.5B'
    }
    


    try:
        # 注意：不再使用files参数，因为我们已经将音频数据包含在data中
        response = requests.post(url, headers=headers, data=data)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        # 尝试解析JSON响应
        try:
            response_json = response.json()
            # 打印完整响应
            print("API响应:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            print(f"原始响应内容: {response.text}")
            # 尝试解决常见的JSON解析问题
            try:
                # 尝试移除可能的BOM标记或特殊字符
                cleaned_text = response.text.strip().lstrip('\ufeff')
                response_json = json.loads(cleaned_text)
                print("修复后成功解析JSON")
            except Exception:
                # 如果仍然失败，尝试按照URI模式提取
                import re
                uri_match = re.search(r'"uri"\s*:\s*"([^"]+)"', response.text)
                if uri_match:
                    uri = uri_match.group(1)
                    print(f"自定义语音上传成功! URI: {uri}")
                    return True
                else:
                    print(f"无法解析响应中的URI")
                    return False
        
        # 检查是否成功
        if response.status_code == 200 and 'result' in response_json and 'uri' in response_json['result']:
            uri = response_json['result']['uri']
            print(f"上传成功! 语音URI: {uri}")
            
            # 将URI保存到文件
            my_voices_path = os.path.join(siliconflow_dir, "my_voices.txt")
            with open(my_voices_path, "a", encoding="utf-8") as f:
                f.write(f"{custom_name}: {uri}\n")
            print(f"URI已保存到 {my_voices_path} 文件")
            
            return True
        else:
            print("上传失败，请检查错误信息")
            return False
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False
    finally:
        # 使用with语句后不需要手动关闭文件
        pass

if __name__ == "__main__":
    main()
