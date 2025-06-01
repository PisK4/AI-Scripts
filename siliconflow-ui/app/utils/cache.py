#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 缓存管理模块
此模块负责管理应用程序的缓存，提高性能和用户体验
"""

import os
import json
import time
import hashlib
from pathlib import Path
import streamlit as st

from app.config import TEMP_DIR

class CacheManager:
    """缓存管理类，负责管理应用程序中的各种缓存"""
    
    def __init__(self):
        """初始化缓存管理器"""
        self.cache_dir = TEMP_DIR / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "index.json"
        self.load_cache_index()
    
    def load_cache_index(self):
        """加载缓存索引"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, "r", encoding="utf-8") as f:
                    self.cache_index = json.load(f)
            except:
                self.cache_index = {"voices": {}, "transcriptions": {}, "last_updated": time.time()}
        else:
            self.cache_index = {"voices": {}, "transcriptions": {}, "last_updated": time.time()}
    
    def save_cache_index(self):
        """保存缓存索引"""
        self.cache_index["last_updated"] = time.time()
        with open(self.cache_index_file, "w", encoding="utf-8") as f:
            json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
    
    def generate_key(self, data):
        """生成缓存键"""
        if isinstance(data, str):
            key = data
        elif isinstance(data, (dict, list)):
            key = json.dumps(data, sort_keys=True)
        else:
            key = str(data)
        
        return hashlib.md5(key.encode()).hexdigest()
    
    def cache_voices(self, voices_data):
        """缓存语音列表数据"""
        cache_key = "voices_list"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(voices_data, f, ensure_ascii=False, indent=2)
        
        self.cache_index["voices"]["list"] = {
            "file": str(cache_file),
            "timestamp": time.time()
        }
        self.save_cache_index()
    
    def get_cached_voices(self):
        """获取缓存的语音列表"""
        if "list" in self.cache_index["voices"]:
            cache_info = self.cache_index["voices"]["list"]
            cache_file = Path(cache_info["file"])
            
            # 检查缓存文件是否存在
            if cache_file.exists():
                # 检查缓存是否过期 (24小时)
                if time.time() - cache_info["timestamp"] < 24 * 60 * 60:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
        
        return None
    
    def cache_transcription(self, audio_path, result):
        """缓存转录结果"""
        # 生成缓存键
        file_hash = self.generate_key(audio_path)
        cache_file = self.cache_dir / f"transcription_{file_hash}.json"
        
        # 保存缓存文件
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 更新缓存索引
        self.cache_index["transcriptions"][file_hash] = {
            "file": str(cache_file),
            "original_path": audio_path,
            "timestamp": time.time()
        }
        self.save_cache_index()
    
    def get_cached_transcription(self, audio_path):
        """获取缓存的转录结果"""
        file_hash = self.generate_key(audio_path)
        
        if file_hash in self.cache_index["transcriptions"]:
            cache_info = self.cache_index["transcriptions"][file_hash]
            cache_file = Path(cache_info["file"])
            
            # 检查缓存文件是否存在
            if cache_file.exists():
                # 检查音频文件是否被修改
                audio_mtime = os.path.getmtime(audio_path) if os.path.exists(audio_path) else 0
                if audio_mtime <= cache_info["timestamp"]:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        return json.load(f)
        
        return None
    
    def clear_expired_cache(self, max_age=7):
        """清理过期缓存（默认7天）"""
        now = time.time()
        max_age_seconds = max_age * 24 * 60 * 60
        
        # 清理转录缓存
        expired_transcriptions = []
        for file_hash, cache_info in self.cache_index["transcriptions"].items():
            if now - cache_info["timestamp"] > max_age_seconds:
                cache_file = Path(cache_info["file"])
                if cache_file.exists():
                    cache_file.unlink()
                expired_transcriptions.append(file_hash)
        
        # 从索引中移除过期项
        for file_hash in expired_transcriptions:
            del self.cache_index["transcriptions"][file_hash]
        
        # 如果有清理，保存更新后的索引
        if expired_transcriptions:
            self.save_cache_index()
            return len(expired_transcriptions)
        
        return 0

# 创建全局缓存管理器实例
cache_manager = CacheManager()

# Streamlit缓存装饰器
@st.cache_data(ttl=3600)
def cached_api_call(func_name, *args, **kwargs):
    """通用API调用缓存装饰器"""
    # 这个函数可以通过传入函数名和参数来缓存任何API调用
    # 由于使用了st.cache_data，Streamlit会自动处理缓存逻辑
    return {"func": func_name, "args": args, "kwargs": kwargs, "timestamp": time.time()}
