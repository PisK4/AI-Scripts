"""
SiliconFlow语音工具集 - 工具模块包
包含各种音频处理工具的功能模块
"""

# 导出所有工具模块
from .audio_converter import show_audio_converter
from .audio_splitter_merger import show_audio_splitter_merger
from .audio_renamer import show_audio_renamer
from .batch_processor import show_batch_processor

# 检查工具依赖是否已安装
import importlib

TOOL_DEPENDENCIES_INSTALLED = True
MISSING_DEPENDENCIES = []

# 检查pydub
try:
    importlib.import_module('pydub')
except ImportError as e:
    TOOL_DEPENDENCIES_INSTALLED = False
    MISSING_DEPENDENCIES.append(f"pydub: {str(e)}")
