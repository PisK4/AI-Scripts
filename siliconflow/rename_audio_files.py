#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件名简化工具

这个脚本用于将复杂的音频文件名简化为更简洁的形式，
例如将"阿狸_[cut_23sec].wav"转换为"阿狸.wav"。
"""

import os
import re
import sys
import shutil
from pathlib import Path


def simplify_filename(filepath):
    """
    简化文件名，提取主要名称部分
    
    Args:
        filepath: 原始文件路径
        
    Returns:
        简化后的文件路径
    """
    # 获取文件的目录、文件名和扩展名
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    # 使用正则表达式提取主要名称（去除下划线后面的内容）
    # 匹配模式：提取直到第一个下划线、空格或方括号的内容
    main_name = re.sub(r'([^_\[\s]+).*', r'\1', name)
    
    # 构建新的文件路径
    new_filename = f"{main_name}{ext}"
    new_filepath = os.path.join(directory, new_filename)
    
    return new_filepath


def rename_file(filepath, dry_run=False, remove_original=True):
    """
    重命名文件
    
    Args:
        filepath: 原始文件路径
        dry_run: 如果为True，只显示会进行的更改，不实际重命名
        remove_original: 如果为True，重命名成功后删除原始文件
        
    Returns:
        成功则返回新文件路径，失败则返回None
    """
    if not os.path.exists(filepath):
        print(f"错误: 文件 '{filepath}' 不存在")
        return None
    
    new_filepath = simplify_filename(filepath)
    
    # 如果新旧文件名相同，则不需要重命名
    if os.path.abspath(filepath) == os.path.abspath(new_filepath):
        print(f"信息: 文件 '{filepath}' 已经是简化名称")
        return filepath
    
    # 检查目标文件是否已存在
    if os.path.exists(new_filepath):
        print(f"警告: 目标文件 '{new_filepath}' 已存在，跳过重命名")
        return None
    
    # 执行重命名
    if dry_run:
        print(f"将重命名: '{filepath}' -> '{new_filepath}'")
        if remove_original:
            print(f"将删除原文件: '{filepath}'")
        return new_filepath
    else:
        try:
            # 复制文件
            shutil.copy2(filepath, new_filepath)
            print(f"已重命名: '{filepath}' -> '{new_filepath}'")
            
            # 如果需要，删除原文件
            if remove_original:
                os.remove(filepath)
                print(f"已删除原文件: '{filepath}'")
                
            return new_filepath
        except Exception as e:
            print(f"操作失败: {str(e)}")
            return None


def process_directory(directory, recursive=False, dry_run=False, remove_original=True):
    """
    处理目录中的所有音频文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归处理子目录
        dry_run: 如果为True，只显示会进行的更改，不实际重命名
    """
    if not os.path.isdir(directory):
        print(f"错误: '{directory}' 不是有效目录")
        return
    
    # 音频文件扩展名
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        # 处理当前目录中的音频文件
        for file in files:
            filepath = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            if ext.lower() in audio_extensions:
                rename_file(filepath, dry_run, remove_original)
        
        # 如果不递归处理，则退出循环
        if not recursive:
            break


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简化音频文件名')
    parser.add_argument('path', help='文件或目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-d', '--dry-run', action='store_true', help='只显示将进行的更改，不实际重命名')
    parser.add_argument('-k', '--keep', action='store_true', help='保留原始文件，不删除')
    
    args = parser.parse_args()
    
    path = os.path.abspath(args.path)
    remove_original = not args.keep  # 如果没有--keep参数，则删除原文件
    
    if os.path.isfile(path):
        rename_file(path, args.dry_run, remove_original)
    elif os.path.isdir(path):
        process_directory(path, args.recursive, args.dry_run, remove_original)
    else:
        print(f"错误: 路径 '{path}' 不存在")
        sys.exit(1)


if __name__ == "__main__":
    main()
