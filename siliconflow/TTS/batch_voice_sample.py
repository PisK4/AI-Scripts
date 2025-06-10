#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量生成语音样本工具
使用指定的音色列表文件，为每个音色生成统一文本的语音样本
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 导入语音生成模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from voice_create import generate_speech

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="批量生成语音样本")
    parser.add_argument("-i", "--input", default="/Users/pis/workspace/AI/ai-scripts/siliconflow/TTS/raw_text_files/CN.json",
                        help="音色列表JSON文件路径")
    parser.add_argument("-o", "--output_dir", default="/Users/pis/workspace/AI/ai-scripts/siliconflow/TTS/audio_sample/CN-2",
                        help="输出目录路径")
    parser.add_argument("-f", "--format", default="wav", choices=["mp3", "wav"], 
                        help="输出音频格式 (默认: wav)")
    parser.add_argument("--model", default="FunAudioLLM/CosyVoice2-0.5B",
                        help="使用的语音模型")
    parser.add_argument("-r", "--rate", type=int, default=44100, 
                        help="采样率 (默认: 44100)")
    parser.add_argument("-s", "--speed", type=float, default=1.0, 
                        help="语速 (默认: 1.0)")
    parser.add_argument("-g", "--gain", type=int, default=-2,  # 降低爆音，默认-2
                        help="增益 (默认: -2)")
    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 音色列表文件不存在: {args.input}")
        return False

    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    # 加载音色列表
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            voices_data = json.load(f)
    except Exception as e:
        print(f"错误: 读取音色列表文件失败: {str(e)}")
        return False

    # 统一的文本模板
    text_template = "hello~hello~[breath]听得到吗？[breath]きこえていますか？初次见面，请多关照呀！这里是<strong>{audio_name_raw}</strong>,是你们最甜甜甜的小草莓"
    # text_template = "英语<|endofprompt|>Hey everyone~ Hey![breath]Can you hear me clearly?[breath]Lovely to meet you all! I'm your<strong>Strawberry-chan</strong>,favorite bilingual sweetheart ever!"

    # 计数器
    total_voices = len(voices_data)
    success_count = 0
    failed_count = 0

    print(f"开始处理总计 {total_voices} 个音色...")

    # 遍历音色列表，生成语音样本
    for name, voice_info in voices_data.items():
        audio_name_raw = voice_info.get("audio_name_raw")
        uri = voice_info.get("uri")
        
        if not audio_name_raw or not uri:
            print(f"警告: 音色信息不完整，跳过: {name}")
            failed_count += 1
            continue
        
        # 替换模板中的变量
        text = text_template.replace("{audio_name_raw}", audio_name_raw)
        
        # 设置输出文件路径
        output_file = os.path.join(args.output_dir, f"{audio_name_raw}.{args.format}")
        
        print(f"\n[{success_count + failed_count + 1}/{total_voices}] 正在处理音色: {audio_name_raw}")
        
        # 生成语音文件
        success = generate_speech(
            text=text,
            voice_uri=uri,
            output_file=output_file,
            model=args.model,
            response_format=args.format,
            sample_rate=args.rate,
            speed=args.speed,
            gain=args.gain
        )
        
        if success:
            success_count += 1
            print(f"✅ 成功生成: {output_file}")
        else:
            failed_count += 1
            print(f"❌ 生成失败: {audio_name_raw}")
    
    # 输出处理结果
    print("\n===== 处理完成 =====")
    print(f"总计音色: {total_voices}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"成功率: {success_count/total_voices*100:.2f}%")
    print(f"所有生成的音频文件已保存到: {args.output_dir}")

if __name__ == "__main__":
    main()
