# 语音转文本工具 (STT - Speech to Text)

这个项目提供了一个简单易用的语音转文本工具，利用SiliconFlow的API将音频文件转换为文本。

## 功能特点

- 支持单个音频文件的转换
- 支持批量处理整个目录中的音频文件
- 自动保存转录结果到文本文件
- 支持多种音频格式（.wav, .mp3, .ogg, .flac, .m4a）

## 安装与设置

### 准备工作

1. 确保你已经安装了Python 3.6或更高版本
2. 获取SiliconFlow API的访问令牌

### 设置虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在Windows上:
venv\Scripts\activate
# 在macOS/Linux上:
source venv/bin/activate

# 安装依赖
pip install requests
```

## 使用方法

### 命令行参数

```
# 处理单个文件
python audio_transcription.py <音频文件路径> [<API令牌>]

# 处理整个目录
python audio_transcription.py --dir <目录路径> [<API令牌>]
```

### 环境变量设置

可以通过设置环境变量`SILICONFLOW_API_TOKEN`来提供API令牌，而不是在命令行中传递：

```bash
# 在macOS/Linux上:
export SILICONFLOW_API_TOKEN="你的API令牌"

# 在Windows上:
set SILICONFLOW_API_TOKEN=你的API令牌
```

### 示例

```bash
# 处理单个文件
python audio_transcription.py /path/to/audio.wav

# 处理整个目录
python audio_transcription.py --dir /path/to/audio/directory
```

## 输出

- 对于单个文件处理，转录结果会直接显示在控制台
- 对于目录处理，每个音频文件的转录结果将保存为相同名称的.txt文件

## 故障排除

- 如果遇到API请求错误，请检查API令牌是否正确
- 确保音频文件格式受支持且文件完好无损

## 项目结构

- `audio_transcription.py`: 主Python脚本
- `audio_transcription.sh`: 原始Shell脚本版本
- `README.md`: 项目文档
