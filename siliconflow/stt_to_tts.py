#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语音处理一体化工具

这个脚本实现了完整的语音处理流程：
1. 首先将音频文件转换为文本（语音识别，STT）
2. 然后使用识别的文本创建自定义语音（语音合成，TTS）

使用方法：
    单个文件处理：
    python stt_to_tts.py <音频文件路径>
    python stt_to_tts.py audios/CN素材/迪丽热巴.wav 
    
    整个目录批量处理：
    python stt_to_tts.py -d <音频目录路径>
    python stt_to_tts.py -d audios/CN素材
"""

import os
import sys
import subprocess
import importlib.util
import re
import argparse
import glob
from pathlib import Path
import tempfile
import time
import json
import unicodedata
import shutil

# 导入拼音转换库
try:
    from pypinyin import lazy_pinyin, Style
except ImportError:
    print("警告: 缺少pypinyin库，正在安装...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pypinyin"])
    from pypinyin import lazy_pinyin, Style


def load_module_from_path(module_name, file_path):
    """
    从指定路径加载Python模块
    
    参数:
        module_name (str): 模块名称
        file_path (str): 模块文件路径
        
    返回:
        module: 加载的模块对象
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def filter_text(text):
    """
    过滤文本，只保留各种语言的文字、标点符号等有用信息，去除emoji和特殊字符
    支持中文、日文、韩文、印尼文等各种语言的文字和标点符号，同时保留英文单词间的空格
    """
    if not text:
        return ""
    
    # 步骤1: 先直接移除常见特殊符号（采用直接替换而非正则）
    filtered_text = text
    
    # 直接替换音乐符号
    filtered_text = filtered_text.replace("🎼", "")  # 音乐符号
    filtered_text = filtered_text.replace("🎵", "")
    filtered_text = filtered_text.replace("🎶", "")
    filtered_text = filtered_text.replace("♫", "")
    filtered_text = filtered_text.replace("♪", "")
    
    # 简单处理几个常见表情符号（使用直接替换而非复杂正则，避免正则过滤中文）
    filtered_text = filtered_text.replace("😊", "")
    filtered_text = filtered_text.replace("😄", "")
    filtered_text = filtered_text.replace("😃", "")
    filtered_text = filtered_text.replace("😀", "")
    filtered_text = filtered_text.replace("😁", "")
    filtered_text = filtered_text.replace("😆", "")
    filtered_text = filtered_text.replace("😅", "")
    filtered_text = filtered_text.replace("🤣", "")
    filtered_text = filtered_text.replace("😂", "")
    filtered_text = filtered_text.replace("🙂", "")
    filtered_text = filtered_text.replace("🙃", "")
    filtered_text = filtered_text.replace("😉", "")
    filtered_text = filtered_text.replace("😌", "")
    filtered_text = filtered_text.replace("😍", "")
    filtered_text = filtered_text.replace("😘", "")
    filtered_text = filtered_text.replace("😗", "")
    filtered_text = filtered_text.replace("😙", "")
    filtered_text = filtered_text.replace("😚", "")
    filtered_text = filtered_text.replace("😋", "")
    filtered_text = filtered_text.replace("😛", "")
    filtered_text = filtered_text.replace("😝", "")
    filtered_text = filtered_text.replace("😜", "")
    filtered_text = filtered_text.replace("🤪", "")
    filtered_text = filtered_text.replace("🤨", "")
    filtered_text = filtered_text.replace("🧐", "")
    filtered_text = filtered_text.replace("🤓", "")
    filtered_text = filtered_text.replace("😎", "")
    filtered_text = filtered_text.replace("🤩", "")
    filtered_text = filtered_text.replace("😏", "")
    filtered_text = filtered_text.replace("😒", "")
    filtered_text = filtered_text.replace("😞", "")
    filtered_text = filtered_text.replace("😔", "")  # 常见的忧伤表情
    filtered_text = filtered_text.replace("😟", "")
    filtered_text = filtered_text.replace("😕", "")
    filtered_text = filtered_text.replace("🙁", "")
    filtered_text = filtered_text.replace("😮", "")  # 惊讶表情
    filtered_text = filtered_text.replace("😯", "")
    filtered_text = filtered_text.replace("😲", "")
    filtered_text = filtered_text.replace("😳", "")
    filtered_text = filtered_text.replace("🥺", "")
    filtered_text = filtered_text.replace("😦", "")
    filtered_text = filtered_text.replace("😧", "")
    filtered_text = filtered_text.replace("😨", "")
    filtered_text = filtered_text.replace("😰", "")
    filtered_text = filtered_text.replace("😱", "")
    filtered_text = filtered_text.replace("😖", "")
    filtered_text = filtered_text.replace("😣", "")
    filtered_text = filtered_text.replace("😞", "")
    filtered_text = filtered_text.replace("😓", "")
    filtered_text = filtered_text.replace("😩", "")
    filtered_text = filtered_text.replace("😫", "")
    filtered_text = filtered_text.replace("😤", "")
    filtered_text = filtered_text.replace("😡", "")  # 生气表情
    filtered_text = filtered_text.replace("😠", "")
    filtered_text = filtered_text.replace("🤬", "")
    
    # 步骤2: 规范化空白字符（不完全移除）
    # 将多个连续空白字符替换为一个空格，保留单词间的分隔
    filtered_text = re.sub(r'\s+', ' ', filtered_text)
    # 去除首尾空格
    filtered_text = filtered_text.strip()
    
    # 步骤3: 输出过滤过程中的调试信息
    print(f"过滤前文本长度: {len(text)}")
    print(f"过滤后文本长度: {len(filtered_text)}")
    
    # 检查过滤后的文本是否为空
    if filtered_text:
        # 显示前20个字符作为预览
        preview = filtered_text[:20] + "..." if len(filtered_text) > 20 else filtered_text
        print(f"过滤后文本: {preview}")
        return filtered_text
    else:
        # 如果过滤后为空，则返回原文本
        print(f"过滤失败，使用原文本: {text[:30]}...")
        return text


def save_to_cn_list(audio_name_raw, audio_name, text, uri):
    """
    将转录文本和音色信息保存到cn_list.json文件
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # cn_list.json文件路径
    # 时间戳+名字
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    json_file_path = os.path.join(project_root, "TTS", "raw_text_files", f"{timestamp}_{audio_name}.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    # 读取现有数据（如果文件存在）
    data = {}
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"警告: {json_file_path} 格式错误，将创建新文件")
    
    # 添加或更新数据
    data[audio_name_raw] = {
        "audio_name_raw": audio_name_raw,
        "audio_name": audio_name,
        "text": text,
        "uri": uri
    }
    
    # 写入文件
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"音色信息已保存到 {json_file_path}")
    return True


def get_audio_duration(file_path):
    """获取音频文件的时长（秒）"""
    try:
        # 使用ffprobe获取音频时长
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            file_path
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return float(output)
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"警告: 无法获取音频时长，将使用完整音频: {str(e)}")
        return None

def trim_audio(input_file, output_file, duration=10.0):
    """截取音频文件的前N秒"""
    try:
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-t", str(duration),
            "-c:a", "copy",
            "-y",  # 覆盖输出文件（如果存在）
            output_file
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"警告: 音频截取失败: {str(e)}")
        return False

def process_audio_file(audio_file_path, is_batch=False, batch_dir_name=None):
    """处理单个音频文件的完整流程"""
    # 检查音频文件是否存在
    if not os.path.isfile(audio_file_path):
        print(f"错误: 文件 '{audio_file_path}' 不存在")
        return False
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 获取音频文件名(不带扩展名)
    audio_name_raw = os.path.splitext(os.path.basename(audio_file_path))[0]
    audio_extension = os.path.splitext(audio_file_path)[1]
    
    # 检测是否含有中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', audio_name_raw))
    
    if has_chinese:
        # 将中文转换为拼音，使用下划线连接
        pinyin_list = lazy_pinyin(audio_name_raw, style=Style.NORMAL)
        audio_name = '_'.join(pinyin_list)
        print(f"注意: 检测到中文名称 '{audio_name_raw}'，已转换为拼音: '{audio_name}'")
    else:
        # 如果没有中文，保留原始名称但进行字符过滤
        audio_name = re.sub(r'[^a-zA-Z0-9_-]', '_', audio_name_raw)
    
    # 确保名称不超过64个字符
    audio_name = audio_name[:64]
    
    print(f"\n======= 处理音频文件 =======")
    print(f"文件路径: {audio_file_path}")
    print(f"原始音频名称: {audio_name_raw}")
    print(f"处理后的名称: {audio_name}")
    
    # 在STT前截取音频（如果需要）
    audio_to_process = audio_file_path
    temp_audio = None
    try:
        # 获取音频时长
        duration = get_audio_duration(audio_file_path)
        if duration is not None and duration > 10.0:
            print(f"\n【预处理：截取音频】")
            print(f"原始音频时长: {duration:.2f}秒，将截取前10秒进行处理")
            
            # 创建临时文件用于存储截取后的音频
            temp_audio = os.path.join(tempfile.gettempdir(), f"trimmed_{int(time.time())}{audio_extension}")
            
            # 截取音频前10秒
            if trim_audio(audio_file_path, temp_audio):
                audio_to_process = temp_audio
                print(f"音频截取成功，使用截取后的音频进行后续处理")
            else:
                print(f"音频截取失败，将使用原始音频")
    except Exception as e:
        print(f"音频截取过程中发生错误: {str(e)}，将使用原始音频")
    
    # 第一步：语音转文本 (STT)
    print(f"\n【第一步：语音转文本】")
    
    # 导入STT模块
    stt_path = os.path.join(project_root, "STT", "audio_transcription.py")
    stt_module = load_module_from_path("audio_transcription", stt_path)
    
    # 执行语音转文本
    print(f"正在处理音频文件: {os.path.basename(audio_file_path)}")
    print(f"正在将音频转换为文本...")
    result = stt_module.transcribe_audio(audio_to_process)
    
    if not result:
        print("错误: 语音转文本失败")
        return False
    
    # 获取转录文本
    transcription = result.get('text', '')
    
    if not transcription:
        print("错误: 未能获取到有效的转录文本")
        return False
    
    # 过滤文本，去除emoji等无用字符
    filtered_transcription = filter_text(transcription)
    print(f"转录成功!")
    print(f"原始文本: {transcription}")
    print(f"过滤后文本: {filtered_transcription}")
    
    # 第二步：使用转录文本创建自定义语音 (TTS)
    print(f"\n【第二步：上传自定义语音】")
    
    # 创建一个临时脚本来运行voice_upload.py
    with tempfile.NamedTemporaryFile(suffix='.sh', mode='w+', delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(f"""#!/bin/bash
cd "{project_root}"
python TTS/voice_upload.py "{audio_file_path}" "{audio_name}" "{filtered_transcription}"
""")
    
    # 设置执行权限
    os.chmod(tmp_path, 0o755)
    
    # 执行临时脚本
    print(f"正在上传自定义语音...")
    uri = None
    try:
        # 执行脚本并获取输出
        result = subprocess.run([tmp_path], check=True, capture_output=True, text=True)
        output = result.stdout
        
        # 尝试从输出中提取URI
        uri_match = re.search(r'speech:[\w-]+:[\w]+:[\w]+', output)
        if uri_match:
            uri = uri_match.group(0)
        
        print(f"语音上传成功! 自定义语音名称: {audio_name}")
        
        # 如果没有找到URI，尝试从voices.json中获取
        if not uri:
            # 先刷新音色列表
            print("未在输出中找到URI，尝试从voices.json获取...")
            fetch_path = os.path.join(project_root, "TTS", "voice_fetch.py")
            subprocess.run(["python", fetch_path], check=True)
            
            # 读取voices.json
            voices_json_path = os.path.join(project_root, "voices.json")
            if os.path.exists(voices_json_path):
                with open(voices_json_path, "r", encoding="utf-8") as f:
                    voices_data = json.load(f)
                    if "result" in voices_data:
                        for voice in voices_data["result"]:
                            if voice.get("customName") == audio_name:
                                uri = voice.get("uri")
                                break
        
        # 根据处理模式选择保存方法
        if uri:
            if is_batch and batch_dir_name:
                # 批量处理模式，保存到以目录名命名的统一JSON文件
                save_to_batch_json(batch_dir_name, audio_name_raw, audio_name, filtered_transcription, uri)
            else:
                # 单文件处理模式，保存到单独的JSON文件
                save_to_cn_list(audio_name_raw, audio_name, filtered_transcription, uri)
        else:
            print("警告: 未能获取到音色URI，无法保存音色信息")
            
    except subprocess.CalledProcessError as e:
        print(f"错误: 语音上传失败 (错误码: {e.returncode})")
        return False
    finally:
        # 删除临时脚本和临时音频文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # 清理临时截取的音频文件
        if temp_audio and os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
            except Exception as e:
                print(f"警告: 无法删除临时音频文件: {str(e)}")
    
    print(f"\n======= 处理完成 =======")
    print(f"原始音频: {audio_file_path}")
    print(f"转录文本: {filtered_transcription}")
    print(f"自定义语音名称: {audio_name}")
    if has_chinese:
        print(f"原始中文名称: {audio_name_raw}")
    if uri:
        print(f"音色URI: {uri}")
    print(f"处理成功!")
    return True


def save_to_batch_json(directory_name, audio_name_raw, audio_name, text, uri):
    """
    将转录文本和音色信息保存到以目录名命名的JSON文件中
    
    参数:
        directory_name: 原始目录名称
        audio_name_raw: 原始音频名称
        audio_name: 处理后的音频名称
        text: 转录文本
        uri: 音色URI
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 确定要保存的JSON文件路径
    json_file_path = os.path.join(project_root, "TTS", "raw_text_files", f"{directory_name}.json")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    # 读取现有数据（如果文件存在）
    data = {}
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"警告: {json_file_path} 格式错误，将创建新文件")
    
    # 添加或更新数据
    data[audio_name_raw] = {
        "audio_name_raw": audio_name_raw,
        "audio_name": audio_name,
        "text": text,
        "uri": uri
    }
    
    # 写入文件
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"音色信息已更新到批量处理文件: {json_file_path}")
    return True

def process_directory(directory_path, audio_extensions=None):
    """批量处理目录中的所有音频文件"""
    if audio_extensions is None:
        audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    # 检查目录是否存在
    if not os.path.isdir(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return False
    
    # 提取目录名（用于保存结果）
    directory_name = os.path.basename(os.path.normpath(directory_path))
    print(f"\n======= 开始批量处理目录 =======")
    print(f"目录路径: {directory_path}")
    print(f"目录名称: {directory_name}")
    
    # 获取目录中的所有音频文件
    audio_files = []
    for ext in audio_extensions:
        pattern = os.path.join(directory_path, f"*{ext}")
        audio_files.extend(glob.glob(pattern))
    
    # 将文件路径按字母排序
    audio_files.sort()
    
    if not audio_files:
        print(f"警告: 目录中没有找到音频文件 (支持的格式: {', '.join(audio_extensions)})")
        return False
    
    print(f"找到 {len(audio_files)} 个音频文件需要处理")
    
    # 保存批量处理的结果集
    batch_results = {}
    
    # 处理统计
    success_count = 0
    failed_count = 0
    
    # 逐个处理音频文件
    for index, audio_file in enumerate(audio_files):
        print(f"\n[{index+1}/{len(audio_files)}] 处理文件: {os.path.basename(audio_file)}")
        # 给process_audio_file函数传递额外的参数，表明这是批量处理
        success = process_audio_file(audio_file, is_batch=True, batch_dir_name=directory_name)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        # 在批处理中添加短暂延迟，避免API请求过于频繁
        if index < len(audio_files) - 1:
            time.sleep(1)
    
    # 打印总结
    print(f"\n======= 批量处理完成 =======")
    print(f"总文件数: {len(audio_files)}")
    print(f"成功处理: {success_count}")
    print(f"处理失败: {failed_count}")
    print(f"所有转录结果已保存至: TTS/raw_text_files/{directory_name}.json")
    
    return success_count > 0


def main():
    """主函数：解析参数并执行相应的处理流程"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='语音处理一体化工具：STT + TTS')
    
    # 定义互斥的参数组（文件或目录）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('file', nargs='?', help='要处理的音频文件路径')
    group.add_argument('-d', '--directory', help='要批量处理的音频文件目录')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据参数执行相应的处理流程
    if args.directory:
        # 批量处理目录
        success = process_directory(args.directory)
        if not success:
            sys.exit(1)
    else:
        # 处理单个文件
        success = process_audio_file(args.file)
        if not success:
            sys.exit(1)
    
    print("\n全部任务已成功完成!")


if __name__ == "__main__":
    main()
