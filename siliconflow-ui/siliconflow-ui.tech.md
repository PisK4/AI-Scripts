# SiliconFlow-UI 技术实现文档

## 项目概述

SiliconFlow-UI 是一个基于 Streamlit 构建的语音处理工具集，提供了包括语音识别、文本转语音、自定义语音和各种音频处理工具的一站式解决方案。项目采用了苹果风格的界面设计，使用体验流畅直观。

## 技术架构

### 基础架构
- **框架**: Streamlit (1.31.0+)
- **语言**: Python 3.8+
- **界面风格**: 苹果设计风格
- **应用结构**: 多页面应用架构

### 核心依赖
- **streamlit**: Web界面框架
- **pandas**: 数据处理和展示
- **pydub**: 音频处理
- **python-dotenv**: 环境变量管理
- **requests**: API请求
- **pypinyin**: 中文转拼音(用于文件命名)
- **matplotlib**: 音频波形可视化

### 目录结构
```
siliconflow-ui/
├── Home.py                  # 主入口文件
├── pages/                   # 功能页面目录
│   ├── 1_speech_recognition.py  # 语音识别
│   ├── 2_custom_voice.py    # 自定义语音
│   ├── 3_text_to_speech.py  # 文本转语音
│   ├── 4_audio_tools.py     # 音频工具箱
│   ├── 5_integrated_processing.py  # 一体化处理
├── app/                     # 核心应用代码
│   ├── components/          # UI组件
│   │   ├── audio_player.py  # 音频播放器
│   │   ├── css.py           # CSS样式定义
│   │   ├── progress.py      # 进度显示组件
│   ├── utils/               # 工具类
│   │   ├── api.py           # API客户端
│   │   ├── state.py         # 状态管理
│   │   ├── cache.py         # 缓存管理
│   ├── config.py            # 配置管理
├── tools/                   # pages 页面中 audio_tools.py 的分页实现
│   ├── audio_converter.py   # 音频转换工具
│   ├── ...
├── audios/                  # 音频文件目录
├── requirements.txt         # 依赖管理
```

## 功能模块

### 1. 语音识别(STT)
- 支持单文件和批量语音转录
- 转录结果实时显示和保存
- 支持多种音频格式

### 2. 文本转语音(TTS)
- 支持多种语音模型选择
- 参数调整(语速、采样率)
- 音频实时预览和下载

### 3. 自定义语音
- 简化版一键创建个性化语音（只需一段音频、名称和文本）
- 多阶段进度显示和状态反馈
- 即创即用，与文本转语音页面无缝集成

### 4. 一体化处理
- 三步式工作流：语音转文本 → 文本编辑 → 文本转语音
- 全程状态保持
- 进度可视化展示

### 5. 音频工具箱
- 格式转换
- 音频分割/合并
- 批量重命名
- 音频提取和处理

## 技术实现要点

### 状态管理
- 使用`StateManager`类统一管理应用状态
- 基于`st.session_state`实现跨页面数据共享
- 各功能模块状态独立管理，确保隔离性

### API集成
- `SiliconFlowAPI`类封装所有API交互
- 支持连接测试和错误处理
- 使用环境变量管理API密钥，确保安全性

### UI组件
- 自定义音频播放器，支持波形显示
- 多阶段进度组件，提供直观的处理进度
- 统一的苹果风格CSS，确保界面美观一致

### 数据流处理
- 基于临时文件处理大型音频
- 内存优化，避免大文件内存溢出
- 处理结果缓存，提高响应速度

## 多页面应用迁移进度

### 已完成页面
- ✅ 主页(Home.py)
- ✅ 语音识别(1_speech_recognition.py)
- ✅ 自定义语音(2_custom_voice.py)
- ✅ 文本转语音(3_text_to_speech.py)
- ✅ 音频工具箱(4_audio_tools.py)
- ✅ 一体化处理(5_integrated_processing.py)

### 迁移优化
- 优化了API状态管理和显示
- 统一了错误处理和提示消息
- 使用一致的苹果风格UI
- 修复了组件间依赖和状态共享问题
- 简化了自定义语音创建流程，提升用户体验

## 下一步优化计划

### 1. 页面命名规范调整
- 移除数字前缀
- 采用纯英文命名，如`speech_recognition.py`

### 2. 用户体验优化
- 添加深色模式支持
- 进一步优化移动端显示
- 统一所有错误和成功提示的样式

### 3. 性能优化
- 增强缓存机制
- 优化大文件处理流程
- 减少页面加载时间

### 4. 代码质量提升
- 添加单元测试
- 实现CI/CD流程
- 代码文档完善

## 开发环境设置

### 基础要求
- Python 3.8+
- FFmpeg (音频处理必需)

### 环境配置
1. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥
```bash
cp .env.example .env
# 编辑.env文件，设置SILICONFLOW_API_KEY
```

4. 运行应用
```bash
streamlit run Home.py
```

## 关键技术点

- Streamlit的多页面应用结构
- 会话状态管理与数据共享
- 组件化UI设计
- RESTful API集成
- 音频处理和流式传输
- 进度可视化与用户反馈
