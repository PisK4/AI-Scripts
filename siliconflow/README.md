# SiliconFlow 语音工具集

这个项目包含了一系列与SiliconFlow语音API交互的工具，可以帮助您轻松实现以下功能：

- **语音识别 (STT)**：将音频文件转换为文本
- **自定义语音 (TTS)**：上传音频创建个人定制语音
- **一体化处理**：从音频转文本再到上传自定义语音的完整流程
- **批量处理**：支持对整个目录的音频文件进行批量处理
- **文件名处理**：简化音频文件名，优化中文名称处理

## 环境准备

1. 确保您已安装Python 3.6或更高版本

2. 安装必要的依赖库：

```bash
pip install python-dotenv requests pypinyin pydub
```

3. 创建`.env`文件，设置必要的API密钥：

```
SILICONFLOW_API_KEY=您的SiliconFlow_API密钥
```

4. 确保安装了`ffmpeg`，用于音频格式转换和处理

### 依赖说明

- **python-dotenv**: 用于从.env文件加载API密钥
- **requests**: 用于发送HTTP请求到SiliconFlow API
- **pypinyin**: 用于将中文名称转换为拼音，适配API要求
- **pydub**: 用于音频处理（如裁剪和格式转换）

## 工具说明

### 1. 语音转文本 (STT)

#### 1.1 音频转录工具 (audio_transcription.py)

这个工具位于`STT`目录下，能够将音频文件转换为文本。

**使用方法**：

```bash
python STT/audio_transcription.py <音频文件路径>
# 或批量处理目录
python STT/audio_transcription.py -d <音频目录路径>
```

**功能**：

- 使用SiliconFlow API进行高精度语音识别
- 支持单文件和目录批量转录
- 自动将转录结果保存为文本文件
- 支持多种音频格式

### 2. 自定义语音 (TTS)

#### 2.1 获取语音列表 (voice_fetch.py)

获取SiliconFlow平台上可用的所有语音列表，并保存为JSON文件。

**使用方法**：
```bash
python TTS/voice_fetch.py
```

**功能**：
- 调用SiliconFlow API获取所有可用语音
- 将结果保存到`voices.json`文件中
- 支持从`.env`文件读取API密钥，增强安全性

#### 2.2 上传自定义语音 (voice_upload.py)

上传音频文件到SiliconFlow平台，创建您自己的定制语音。

**使用方法**：

```bash
python TTS/voice_upload.py <音频文件路径> <自定义语音名称> [<朗读文本>]
```

**参数说明**：

- `<音频文件路径>`: 要上传的音频文件（支持mp3等格式）
- `<自定义语音名称>`: 为您的自定义语音取一个名字
- `[<朗读文本>]`: 可选参数，音频中朗读的文本内容。如不提供，将使用默认文本

**功能特点**：

- 支持大多数音频格式的上传
- 自动将音频裁剪为10秒，以符合API限制
- 将音频转换为Base64格式上传
- 自动处理中文名称，转换为拼音
- 返回可用于TTS的语音URI

**功能**：

- 将您的音频样本上传到SiliconFlow
- 创建自定义语音模型
- 保存语音URI到`my_voices.txt`和`voices.json`文件，方便后续使用

### 3. 一体化工具

#### 3.1 STT和TTS集成工具 (stt_to_tts.py)

这个工具将语音识别和自定义语音上传集成到一个完整的工作流程中。

**使用方法**：

```bash
# 处理单个文件
python stt_to_tts.py <音频文件路径>

# 批量处理目录
python stt_to_tts.py -d <音频目录路径>
```

**功能特点**：

- 自动完成从音频转文本再到上传自定义语音的完整流程
- 支持单文件和整个目录的批量处理
- 自动将中文文件名转换为拼音作为语音名称
- 处理特殊字符，确保语音名称符合API要求
- 显示详细处理日志和批量处理统计

#### 3.2 音频文件名简化工具 (rename_audio_files.py)

这个工具可以简化复杂的音频文件名，例如从“阿狼_[cut_23sec].wav”简化为“阿狼.wav”。

**使用方法**：

```bash
# 处理单个文件
python rename_audio_files.py <音频文件路径>

# 预览模式（不实际重命名）
python rename_audio_files.py <音频文件路径> --dry-run

# 保留原始文件（不删除）
python rename_audio_files.py <音频文件路径> --keep

# 处理整个目录
python rename_audio_files.py <目录路径>

# 递归处理子目录
python rename_audio_files.py <目录路径> --recursive
```

**功能特点**：

- 自动定位和删除文件名中的标记部分（如`[cut_23sec]`）
- 默认删除原始文件，减少存储空间占用
- 支持处理单个文件或整个目录
- 提供预览模式，显示将进行的更改而不实际执行
- 安全处理中文文件名

**功能**：
- 支持多种音频格式（mp3, wav, ogg, flac, m4a等）
- 自动转换为标准WAV格式以提高识别准确率
- 支持长音频分段识别，解决API限制问题
- 保存识别结果到文本文件
- 多重API识别策略，提高识别成功率

## 注意事项

1. 确保`.env`文件中包含必要的API密钥
2. 自定义语音上传时，音频文件会被自动截取10秒，以符合API限制
3. 中文文件名会自动转换为拼音，以适应API要求
4. 如需要简化文件名，可以先使用rename_audio_files.py工具
5. 批量处理时，每个文件之间会有短暂停顿，避免API请求过于频繁

## 故障排除

1. 如遇到“API密钥未设置”错误，请检查`.env`文件是否正确配置
2. 如遇到“文件未找到”错误，可能是文件路径包含特殊字符，请使用引号包裹路径
3. 音频文件太大时，会被自动截取前10秒上传，这是正常行为
4. 如果上传失败，请检查音频格式和文件名是否符合要求
5. 中文文件名会自动转换为拼音，这是因为API只支持英文字符

## 项目结构

```
siliconflow/
├─ .env                     # 环境变量配置文件
├─ stt_to_tts.py            # 语音转文本并上传的一体化工具
├─ rename_audio_files.py    # 音频文件名简化工具
├─ STT/                     # 语音识别工具目录
│   ├─ audio_transcription.py  # 音频转录工具
│   └─ audio_transcription.sh  # 旧版转录脚本(已被Python版本替代)
├─ TTS/                     # 语音合成工具目录
│   ├─ voice_fetch.py         # 获取语音列表工具
│   ├─ voice_upload.py        # 上传自定义语音工具
│   └─ voice_upload.sh        # 旧版上传脚本(已被Python版本替代)
├─ audios/                   # 音频文件目录
│   └─ CN素材/              # 中文音频文件集
├─ voices.json              # 保存的语音列表
└─ my_voices.txt            # 保存的自定义语音URI
```

## 技术简介

该项目利用了以下技术实现音频处理和语音定制：

1. **SiliconFlow API**：用于语音识别和上传自定义语音
2. **Base64编码**：用于将音频文件转换为文本格式传输
3. **Pydub**：处理音频文件，包括裁剪和格式转换
4. **Pypinyin**：将中文转换为拼音以适配API要求

所有工具均支持批量处理，大大提高了效率。
