#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 进度显示组件
提供各种进度展示方式，增强用户体验
"""

import time
import streamlit as st

class BaseProgress:
    """进度显示基类"""
    
    def __init__(self, title=None):
        """
        初始化进度显示
        参数:
            title: 进度标题
        """
        self.title = title
        if title:
            self.title_container = st.empty()
            self.title_container.subheader(title)
        
        # 进度条和状态文本容器
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
        # 初始状态
        self.current_progress = 0
        self.start_time = time.time()
    
    def update(self, progress, status=None):
        """
        更新进度
        参数:
            progress: 0-1之间的进度值
            status: 状态文本
        """
        self.current_progress = progress
        
        # 更新进度条
        self.progress_bar.progress(progress)
        
        # 更新状态文本
        if status:
            self.status_text.text(status)
        
        # 返回自身以支持链式调用
        return self
    
    def complete(self, message="完成!"):
        """
        标记进度完成
        参数:
            message: 完成消息
        """
        self.update(1.0, message)
        
        # 计算耗时
        elapsed = time.time() - self.start_time
        time_str = f"耗时: {elapsed:.2f} 秒"
        
        # 显示完成信息
        st.success(f"{message} {time_str}")
        
        # 清除进度条和状态文本
        self.clear()
    
    def clear(self):
        """清除进度显示"""
        self.progress_bar.empty()
        self.status_text.empty()


class TranscriptionProgress(BaseProgress):
    """语音转录进度展示"""
    
    def __init__(self, title="语音转录进度"):
        """初始化语音转录进度"""
        super().__init__(title)
        
        # 转录特有的状态
        self.processed_files = 0
        self.total_files = 0
    
    def start_batch(self, total_files):
        """
        开始批量处理
        参数:
            total_files: 总文件数
        """
        self.total_files = total_files
        self.processed_files = 0
        self.update(0, f"准备处理 {total_files} 个文件...")
    
    def file_complete(self, file_name, success=True):
        """
        标记一个文件处理完成
        参数:
            file_name: 文件名
            success: 处理是否成功
        """
        self.processed_files += 1
        progress = self.processed_files / self.total_files
        
        status = f"{'✅' if success else '❌'} {file_name} ({self.processed_files}/{self.total_files})"
        self.update(progress, status)
        
        if self.processed_files == self.total_files:
            self.complete(f"所有 {self.total_files} 个文件处理完成!")


class VoiceUploadProgress(BaseProgress):
    """语音上传进度展示"""
    
    def __init__(self, title="语音上传进度"):
        """初始化语音上传进度"""
        super().__init__(title)
        
        # 定义处理阶段
        self.stages = [
            {"name": "准备音频", "weight": 0.1},
            {"name": "优化音频", "weight": 0.2},
            {"name": "上传音频", "weight": 0.4},
            {"name": "创建语音模型", "weight": 0.3}
        ]
        self.current_stage = 0
    
    def next_stage(self):
        """进入下一个处理阶段"""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            
        # 计算当前总进度
        progress = sum(s["weight"] for s in self.stages[:self.current_stage])
        status = f"阶段 {self.current_stage+1}/{len(self.stages)}: {self.stages[self.current_stage]['name']}..."
        
        self.update(progress, status)
    
    def update_stage_progress(self, stage_progress):
        """
        更新当前阶段的进度
        参数:
            stage_progress: 当前阶段的进度(0-1)
        """
        # 计算之前阶段的总权重
        previous_weight = sum(s["weight"] for s in self.stages[:self.current_stage])
        
        # 计算当前阶段的贡献
        current_contribution = self.stages[self.current_stage]["weight"] * stage_progress
        
        # 计算总进度
        total_progress = previous_weight + current_contribution
        
        # 更新进度条
        self.update(total_progress)


class MultiStageProgress:
    """多阶段进度展示"""
    
    def __init__(self, stages, title="处理进度"):
        """
        初始化多阶段进度
        参数:
            stages: 阶段列表，每个元素为字典，包含name和weight
            title: 进度标题
        """
        self.title = title
        self.stages = stages
        self.current_stage_index = 0
        
        # 创建标题
        st.subheader(title)
        
        # 创建阶段列表
        self.stage_containers = []
        for stage in stages:
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
            with col1:
                status = st.empty()
            with col2:
                progress = st.progress(0)
            with col3:
                percentage = st.empty()
            
            self.stage_containers.append({
                "status": status,
                "progress": progress,
                "percentage": percentage,
                "completed": False
            })
            
            # 初始化状态
            status.text("⏳")
            percentage.text("0%")
        
        # 设置当前阶段为活动状态
        self._update_stage_status(0, "🔄")
    
    def _update_stage_status(self, stage_index, icon):
        """更新阶段状态图标"""
        if 0 <= stage_index < len(self.stage_containers):
            self.stage_containers[stage_index]["status"].text(icon)
    
    def update_stage(self, stage_index, progress):
        """
        更新指定阶段的进度
        参数:
            stage_index: 阶段索引
            progress: 进度值(0-1)
        """
        if 0 <= stage_index < len(self.stage_containers):
            # 更新进度条和百分比
            self.stage_containers[stage_index]["progress"].progress(progress)
            self.stage_containers[stage_index]["percentage"].text(f"{int(progress * 100)}%")
            
            # 如果完成，更新状态
            if progress >= 1.0 and not self.stage_containers[stage_index]["completed"]:
                self._update_stage_status(stage_index, "✅")
                self.stage_containers[stage_index]["completed"] = True
                
                # 激活下一阶段
                if stage_index < len(self.stage_containers) - 1:
                    self.current_stage_index = stage_index + 1
                    self._update_stage_status(self.current_stage_index, "🔄")
    
    def complete_all(self):
        """完成所有阶段"""
        for i in range(len(self.stage_containers)):
            self.update_stage(i, 1.0)
        
        st.success(f"{self.title}完成!")
    
    def error(self, stage_index, message):
        """
        标记阶段错误
        参数:
            stage_index: 阶段索引
            message: 错误消息
        """
        if 0 <= stage_index < len(self.stage_containers):
            self._update_stage_status(stage_index, "❌")
            st.error(f"阶段 {stage_index+1} ({self.stages[stage_index]['name']}) 失败: {message}")
            
            # 将后续阶段标记为跳过
            for i in range(stage_index + 1, len(self.stage_containers)):
                self._update_stage_status(i, "⏭️")
    
    def clear(self):
        """清除进度显示"""
        # 将所有容器清空
        for container in self.stage_containers:
            container["status"].empty()
            container["progress"].empty()
            container["percentage"].empty()
