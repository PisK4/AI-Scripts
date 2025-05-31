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
    
    整个目录批量处理：
    python stt_to_tts.py -d <音频目录路径>
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


def process_audio_file(audio_file_path):
    """处理单个音频文件的完整流程"""
    # 检查音频文件是否存在
    if not os.path.isfile(audio_file_path):
        print(f"错误: 文件 '{audio_file_path}' 不存在")
        return False
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 获取音频文件名(不带扩展名)
    audio_name_raw = os.path.splitext(os.path.basename(audio_file_path))[0]
    
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
    
    # 第一步：语音转文本 (STT)
    print(f"\n【第一步：语音转文本】")
    
    # 导入STT模块
    stt_path = os.path.join(project_root, "STT", "audio_transcription.py")
    stt_module = load_module_from_path("audio_transcription", stt_path)
    
    # 执行语音转文本
    print(f"正在将音频转换为文本...")
    result = stt_module.transcribe_audio(audio_file_path)
    
    if not result:
        print("错误: 语音转文本失败")
        return False
    
    # 获取转录文本
    transcription = result.get('text', '')
    
    if not transcription:
        print("错误: 未能获取到有效的转录文本")
        return False
    
    print(f"转录成功! 文本内容: {transcription}")
    
    # 第二步：使用转录文本创建自定义语音 (TTS)
    print(f"\n【第二步：上传自定义语音】")
    
    # 创建一个临时脚本来运行voice_upload.py
    with tempfile.NamedTemporaryFile(suffix='.sh', mode='w+', delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(f"""#!/bin/bash
cd "{project_root}"
python TTS/voice_upload.py "{audio_file_path}" "{audio_name}" "{transcription}"
""")
    
    # 设置执行权限
    os.chmod(tmp_path, 0o755)
    
    # 执行临时脚本
    print(f"正在上传自定义语音...")
    try:
        subprocess.run([tmp_path], check=True)
        print(f"语音上传成功! 自定义语音名称: {audio_name}")
    except subprocess.CalledProcessError as e:
        print(f"错误: 语音上传失败 (错误码: {e.returncode})")
        return False
    finally:
        # 删除临时脚本
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    print(f"\n======= 处理完成 =======")
    print(f"原始音频: {audio_file_path}")
    print(f"转录文本: {transcription}")
    print(f"自定义语音名称: {audio_name}")
    if has_chinese:
        print(f"原始中文名称: {audio_name_raw}")
    print(f"处理成功!")
    return True


def process_directory(directory_path, audio_extensions=None):
    """批量处理目录中的所有音频文件"""
    if audio_extensions is None:
        audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    # 检查目录是否存在
    if not os.path.isdir(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return False
    
    print(f"\n======= 开始批量处理目录 =======")
    print(f"目录路径: {directory_path}")
    
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
    
    # 处理统计
    success_count = 0
    failed_count = 0
    
    # 逐个处理音频文件
    for index, audio_file in enumerate(audio_files):
        print(f"\n[{index+1}/{len(audio_files)}] 处理文件: {os.path.basename(audio_file)}")
        success = process_audio_file(audio_file)
        
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
