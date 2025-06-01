# SiliconFlow语音工具集 - 功能完善版

<div align="center">

![SiliconFlow语音工具集](https://img.shields.io/badge/SiliconFlow-语音工具集-0071e3?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgY2xhc3M9ImZlYXRoZXIgZmVhdGhlci1taWMiPjxwYXRoIGQ9Ik0xMiAxIGE1IDUgMCAwIDEgNSA1IHYgNiBhNSA1IDAgMCAxIC0xMCAwIHYgLTYgYTUgNSAwIDAgMSA1IC01IHoiLz48cGF0aCBkPSJNMTkgMTAgdjIgYTcgNyAwIDAgMSAtMTQgMCB2IC0yIi8+PHBhdGggZD0iTTEyIDIzIGMgMiAwIDIgLTMgNCAtMyBoLTggYzIgMCAyIDMgNCAzIHoiLz48L3N2Zz4=)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)

</div>

> 一个功能完善、界面美观的SiliconFlow API语音工具集，支持语音识别、文本转语音、自定义语音和一系列音频处理工具。

## 📚 项目概述

SiliconFlow语音工具集是一个基于Streamlit开发的Web应用，集成了SiliconFlow API的各种语音功能，为用户提供一站式语音处理解决方案。应用采用苹果设计风格，让使用体验更加流畅、直观。

## ✨ 主要功能

- **语音识别（STT）**：将音频文件转化为文本，支持单文件和批量转录
- **文本转语音（TTS）**：将文本生成为自然流畅的语音，支持多种语音和参数调整
- **自定义语音**：创建和管理个性化语音模型
- **一体化处理**：将语音识别、文本编辑和语音生成集成为完整工作流
- **工具箱**：提供一系列实用的音频处理工具（格式转换、分割/合并、重命名、批量处理等）

## 💾 安装与运行

### 先决条件

- Python 3.8+
- FFmpeg (用于音频处理功能)

### 安装步骤

1. 克隆项目

```bash
git clone https://github.com/your-username/siliconflow-ui.git
cd siliconflow-ui
```

2. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 安装FFmpeg (音频处理必需)

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
下载并安装 [FFmpeg](https://www.ffmpeg.org/download.html).

5. 配置API密钥

```bash
cp .env.example .env
# 编辑.env文件，设置SILICONFLOW_API_KEY
```

6. 运行应用

```bash
python -m streamlit run app/app.py
```

## 1. 项目初始化

### 1.1 目录结构创建

首先创建了基本的项目目录结构：

```
siliconflow-ui/
├── app/                # Web应用相关文件
│   ├── components/     # 自定义组件
│   ├── pages/          # 页面模块
│   └── utils/          # 辅助工具
├── audios/             # 音频文件目录
├── implement.md        # 实现记录文档
└── requirements.txt    # 依赖管理
```

### 1.2 依赖配置

创建`requirements.txt`文件，包含以下依赖：

- streamlit>=1.31.0：Web界面框架
- pandas>=2.0.0：数据处理和展示
- pydub>=0.25.1：音频处理
- python-dotenv>=1.0.0：环境变量管理
- requests>=2.28.0：API请求
- pypinyin>=0.48.0：中文转拼音
- matplotlib>=3.7.0：数据可视化

## 2. 核心文件实现

### 2.1 工具模块实现

已完成以下核心工具模块：

1. **配置文件和环境管理** (`app/config.py`)
   - 实现了环境变量加载和配置
   - 项目路径管理
   - API密钥管理
   - 支持的音频格式定义

2. **API调用封装** (`app/utils/api.py`)
   - SiliconFlowAPI类封装了所有API交互
   - 支持音频转录、语音列表获取、语音上传、语音生成等功能
   - 包含错误处理和状态反馈

3. **缓存管理** (`app/utils/cache.py`)
   - 实现了API结果缓存机制
   - 语音列表缓存
   - 转录结果缓存
   - 缓存过期处理

4. **状态管理** (`app/utils/state.py`)
   - 使用Streamlit的session_state管理应用状态
   - 页面导航状态
   - API连接状态
   - 各功能模块状态管理

### 2.2 组件实现

已完成以下自定义组件：

1. **音频播放器** (`app/components/audio_player.py`)
   - 增强型音频播放器
   - 波形可视化
   - 音频信息显示
   - 支持文件路径或二进制数据

2. **文件上传器** (`app/components/file_uploader.py`)
   - 单个音频文件上传器
   - 多文件批量上传器
   - 文件格式筛选
   - 上传状态反馈

3. **进度显示** (`app/components/progress.py`)
   - 基础进度显示
   - 转录进度显示
   - 语音上传进度显示
   - 多阶段处理进度显示

### 2.3 应用入口和页面结构

已实现的页面和功能：

1. **应用入口** (`app/app.py`)
   - 应用初始化和配置
   - 导航栏和页面路由
   - API状态检测
   - 用户界面风格定制

2. **首页** (`app/pages/home.py`)
   - 功能概览
   - 快速导航卡片
   - 系统状态显示

3. **语音识别页面** (`app/pages/stt.py`)
   - 单个文件转录
   - 批量文件处理
   - 结果预览和导出

4. **文本转语音页面** (`app/pages/tts.py`)
   - 语音模型选择
   - 参数调整
   - 实时生成和预览

5. **自定义语音页面** (`app/pages/voice.py`)
   - 创建自定义语音
   - 管理已创建的语音
   - 音频样本上传和处理

6. **一体化处理页面** (`app/pages/integrated.py`)
   - 完整工作流实现
   - 分步引导
   - 中间结果编辑
   - 结果对比和导出

7. **工具箱页面** (`app/pages/tools.py`) - 已完成
   - 音频格式转换：支持多种音频格式互转，可调整码率和质量
   - 音频分割/合并：可按时间分割或合并多个音频，支持交叉淡入淡出
   - 音频重命名：支持前缀/后缀添加、自定义格式和中文拼音转换
   - 批量处理：支持多种操作同时应用（格式转换、音量调整、速度调整、正规化等）

## 3. 功能完成情况

所有计划的核心功能已全部完成，包括：
1. 语音识别（STT）功能
2. 文本转语音（TTS）功能
3. 自定义语音管理
4. 一体化处理工作流
5. 实用工具箱功能（音频转换、分割/合并、重命名、批量处理）

## 4. 已完成工作进展

1. 已添加启动脚本 `run_app.py`，简化用户使用体验
   - 提供了一键启动应用程序的功能
   - 已集成环境检查，确保 API 密钥正确设置
   - 自动处理路径问题，解决了包导入问题

2. 已修复所有模块的导入问题
   - 使用相对导入方式替代绝对导入方式
   - 解决了循环导入的问题
   - 添加了必要的 `__init__.py` 文件，使 Python 正确识别包结构

3. 补充了环境配置文件
   - 添加了 `.env` 模板文件，便于用户配置 API 密钥
   - 设置了虚拟环境和依赖包管理

## 5. 已解决的问题

1. **导入错误和包识别问题**
   - 添加了 `__init__.py` 文件到 `app`、`utils`、`pages` 和 `components` 目录
   - 将绝对导入改为相对导入或基于项目根目录的导入
   - 使用 `sys.path` 动态调整，确保模块能够正确导入
   - 开发了自动修复导入语句的脚本 (`fix_imports.py` 和 `fix_all_imports.py`)

2. **循环导入问题**
   - 重构了 `app.py` 中页面模块的导入方式，改为在条件块内部导入
   - 确保 `st.set_page_config()` 是第一个被执行的 Streamlit 命令
   - 调整了组件和页面之间的依赖关系，避免循环引用

3. **音频处理依赖问题**
   - 识别出应用程序依赖系统级 `ffmpeg` 工具和 Python `audioop` 模块
   - 在 `audio_player.py` 中添加了优雅的错误处理机制
   - 实现了音频处理不可用时的降级方案，确保应用程序仍能启动和运行
   - 添加了友好的用户提示，指导安装所需依赖

4. **Streamlit API 变更问题**
   - 将过时的 `st.experimental_rerun()` 方法替换为新的 `st.rerun()` 方法
   - 修复了所有页面中的相关 API 调用，包括 `home.py`、`voice.py` 和 `integrated.py`

5. **SiliconFlow API 集成问题**
   - 修正了 API 基础 URL 从 `https://api.siliconflow.ai/v1` 为 `https://api.siliconflow.cn/v1`
   - 更新了所有 API 路径和参数格式，使其与最新的 API 文档保持一致
   - 修正了语音列表获取逻辑，正确处理 `result` 字段的数据
   - 修复了生成语音 API 调用，将 `text` 参数改为 `input`，`format` 改为 `response_format`
   - 在应用启动时添加了主动 API 连接检测和状态显示

## 6. 最新完成的工作

1. **解决音频处理依赖问题**
   - 完善了PyAudio、FFmpeg和其他音频处理组件的安装和配置指南
   - 添加了一键强制尝试功能，方便用户在安装依赖后验证
   - 为FFmpeg工具添加了正确的路径配置，解决在macOS上无法识别的问题
   - 优化了工具箱中音频处理功能的错误处理机制

2. **添加苹果设计风格界面**
   - 创建了完整的自定义CSS主题，遵循苹果设计指南
   - 采用SF Pro字体、圆滑化的圆角和柔和的阴影，增强视觉效果
   - 优化了按钮、表单、卡片、标签页等UI组件的交互体验
   - 添加了平滑过渡动画和悬停效果，提升视觉反馈

3. **增强的错误处理和用户反馈**
   - 添加了详细的错误跟踪功能，显示完整的错误堆栈
   - 为工具箱的各个功能模块添加了异常捕获机制
   - 改进了依赖检查和安装指南，提供针对各操作系统的具体步骤

4. **全面集成测试**
   - 对API集成进行了全面测试，确保与SiliconFlow API的完美对接
   - 验证了主要功能模块的完整性，包括语音识别、文本转语音和音频处理
   - 测试了各种异常情况的错误处理和用户反馈

## 7. 继续改进计划

1. **多语言支持**
   - 添加国际化框架，支持中文/英文切换
   - 为所有页面和组件添加多语言翻译

2. **跨平台完善**
   - 测试并适配不同操作系统（Windows/Linux/macOS）
   - 完善移动端响应式设计
   - 添加离线处理能力

3. **性能优化**
   - 优化大文件处理性能
   - 提升批量处理的速度和稳定性
   - 添加缓存机制减少API调用

4. **高级功能**
   - 添加音频波形可视化展示
   - 集成人工智能生成文本功能
   - 添加音频分析和数据分析功能

## 8. 继续安装开发环境

如果您在某些系统上遇到了音频依赖问题，可以尝试以下更全面的安装步骤：

### macOS完整安装

```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装FFmpeg和PortAudio
 brew install ffmpeg portaudio

# 在虚拟环境中安装Python依赖
 source venv/bin/activate
 pip install --upgrade pip
 pip install pyaudio pydub ffmpeg-python wave numpy
```

### Linux (Ubuntu/Debian)完整安装

```bash
# 安装系统依赖
 sudo apt-get update
 sudo apt-get install -y python3-dev portaudio19-dev libavcodec-extra ffmpeg

# 在虚拟环境中安装Python依赖
 source venv/bin/activate
 pip install --upgrade pip
 pip install pyaudio pydub ffmpeg-python wave numpy
```

### Windows完整安装

1. 下载并安装 [FFmpeg](https://www.ffmpeg.org/download.html)
2. 将FFmpeg添加到系统PATH
3. 安装Python依赖：
```bash
.\venv\Scripts\activate
pip install --upgrade pip
pip install pyaudio pydub ffmpeg-python wave numpy
```

## 9. 项目相关链接

- [SiliconFlow官网](https://www.siliconflow.cn)
- [SiliconFlow API文档](https://www.siliconflow.cn/docs)
- [Streamlit官方文档](https://docs.streamlit.io)
   - 批处理任务队列和后台处理
   - 更多音频效果（均衡器、降噪、混响等）
   - 多语言界面支持
   - Python 版本兼容性检查和提示

## 7. 启动与使用指南

### 7.1 环境准备

1. **Python 环境**
   - 推荐使用 Python 3.9-3.12 版本
   - Python 3.13 可能存在 `audioop` 模块兼容性问题

2. **系统依赖**
   - 安装 FFmpeg：`brew install ffmpeg`（macOS）或 `apt install ffmpeg`（Ubuntu/Debian）
   - 安装 xcode 命令行工具（macOS）：`xcode-select --install`

3. **Python 依赖**
   - 创建虚拟环境：`python -m venv venv`
   - 激活环境：`source venv/bin/activate`
   - 安装依赖：`pip install -r requirements.txt`

### 7.2 应用启动

1. **配置 API 密钥**
   - 复制 `.env.template` 为 `.env`
   - 编辑 `.env` 文件，添加你的 SiliconFlow API 密钥

2. **启动应用**
   - 使用启动脚本：`python run_app.py`
   - 打开浏览器访问：`http://localhost:8501`

### 7.3 使用说明

应用程序提供以下主要功能：

1. **语音识别**：将音频文件转换为文本
2. **文本转语音**：使用预设或自定义语音生成语音文件
3. **自定义语音**：上传音频样本创建个性化语音
4. **一体化处理**：从音频转文本到文本生成语音的完整工作流
5. **工具箱**：音频格式转换、分割合并、批量处理等实用工具
