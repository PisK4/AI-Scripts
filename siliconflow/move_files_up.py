#!/usr/bin/env python3
"""
文件上移工具

这个脚本用于将子文件夹中的文件移动到上一级目录。
主要用于音频文件的整理，避免过深的目录结构。

使用方法:
    python move_files_up.py <目录路径>
    
示例:
    python move_files_up.py "audios/EN 声优_V1"
"""

import os
import sys
import shutil
from pathlib import Path


def move_files_up(directory):
    """
    将指定目录下所有子文件夹中的文件移动到该目录
    
    参数:
        directory (str): 要处理的目录路径
    """
    # 确保目录存在
    if not os.path.isdir(directory):
        print(f"错误: 目录 '{directory}' 不存在")
        return False
    
    # 获取目录的绝对路径
    directory = os.path.abspath(directory)
    print(f"\n==== 开始处理目录: {directory} ====")
    
    # 统计信息
    total_files = 0
    moved_files = 0
    skipped_files = 0
    renamed_files = 0
    
    # 遍历目录中的所有子文件夹
    for root, dirs, files in os.walk(directory):
        # 跳过根目录中的文件
        if root == directory:
            continue
        
        # 获取子文件夹名称（用于处理重名）
        subfolder = os.path.basename(root)
        
        # 处理当前文件夹中的所有文件
        for file in files:
            # 跳过隐藏文件和系统文件
            if file.startswith('.'):
                continue
                
            total_files += 1
            
            # 源文件和目标文件的完整路径
            source_path = os.path.join(root, file)
            target_path = os.path.join(directory, file)
            
            # 检查是否会重名
            if os.path.exists(target_path):
                # 文件已存在，使用"文件夹名_文件名.扩展名"的方式重命名
                filename, extension = os.path.splitext(file)
                new_filename = f"{filename}{extension}"
                target_path = os.path.join(directory, new_filename)
                
                # 如果重命名后仍然存在，则添加数字后缀
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{subfolder}_{filename}_{counter}{extension}"
                    target_path = os.path.join(directory, new_filename)
                    counter += 1
                
                print(f"文件名冲突: '{file}' 重命名为 '{os.path.basename(target_path)}'")
                renamed_files += 1
            
            try:
                # 移动文件
                shutil.move(source_path, target_path)
                print(f"已移动: {os.path.relpath(source_path, directory)} -> {os.path.basename(target_path)}")
                moved_files += 1
            except Exception as e:
                print(f"移动失败: {os.path.relpath(source_path, directory)} - {str(e)}")
                skipped_files += 1
    
    # 处理可能产生的空文件夹
    empty_folders = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        # 跳过根目录
        if root == directory:
            continue
            
        # 检查文件夹是否为空（不包括隐藏文件）
        has_visible_files = False
        for item in os.listdir(root):
            if not item.startswith('.'):
                has_visible_files = True
                break
        
        # 如果文件夹为空，删除它
        if not has_visible_files:
            try:
                # 移除文件夹（即使包含隐藏文件也移除）
                shutil.rmtree(root)
                print(f"已删除空文件夹: {os.path.relpath(root, directory)}")
                empty_folders += 1
            except Exception as e:
                print(f"删除文件夹失败: {os.path.relpath(root, directory)} - {str(e)}")
    
    # 打印总结
    print(f"\n==== 处理完成 ====")
    print(f"总文件数: {total_files}")
    print(f"成功移动: {moved_files}")
    print(f"重命名: {renamed_files}")
    print(f"跳过: {skipped_files}")
    print(f"删除空文件夹: {empty_folders}")
    
    return moved_files > 0


def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <目录路径>")
        print(f"示例: {sys.argv[0]} \"audios/EN 声优_V1\"")
        return
    
    # 获取目录路径
    directory = sys.argv[1]
    
    # 移动文件
    move_files_up(directory)


if __name__ == "__main__":
    main()
