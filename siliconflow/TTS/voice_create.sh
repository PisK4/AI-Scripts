#!/bin/bash

# SiliconFlow TTS 语音生成工具 (Shell版本)
# 使用SiliconFlow API将文本转换为语音并保存为音频文件

# 加载API密钥
if [ -f "../.env" ]; then
    # 解析.env文件中的SILICONFLOW_API_KEY
    SILICONFLOW_API_KEY=$(grep SILICONFLOW_API_KEY ../.env | cut -d '=' -f2)
fi

if [ -z "$SILICONFLOW_API_KEY" ]; then
    echo "错误: 未找到SILICONFLOW_API_KEY环境变量。请在.env文件中设置。"
    exit 1
fi

# 默认参数
MODEL="FunAudioLLM/CosyVoice2-0.5B"
RESPONSE_FORMAT="mp3"
SAMPLE_RATE=32000
SPEED=1
GAIN=0
STREAM="false"
OUTPUT_FILE="output.mp3"

# 帮助信息
show_help() {
    echo "用法: $0 [选项] <文本> <语音URI>"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示帮助信息"
    echo "  -m, --model MODEL       使用的模型名称 (默认: $MODEL)"
    echo "  -f, --format FORMAT     输出格式 (mp3或wav, 默认: $RESPONSE_FORMAT)"
    echo "  -r, --rate RATE         采样率 (默认: $SAMPLE_RATE)"
    echo "  -s, --speed SPEED       语速 (默认: $SPEED)"
    echo "  -g, --gain GAIN         增益 (默认: $GAIN)"
    echo "  -o, --output FILE       输出文件路径 (默认: $OUTPUT_FILE)"
    echo "  --stream                启用流式模式 (默认关闭)"
    echo ""
    echo "示例:"
    echo "  $0 '你好，世界' 'speech:2B:ag5cthth2f:kvfcdsgyrbcyruvitvvp'"
    echo "  $0 -o hello.mp3 -s 1.2 '你好，世界' 'speech:2B:ag5cthth2f:kvfcdsgyrbcyruvitvvp'"
    exit 0
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -f|--format)
            RESPONSE_FORMAT="$2"
            shift 2
            ;;
        -r|--rate)
            SAMPLE_RATE="$2"
            shift 2
            ;;
        -s|--speed)
            SPEED="$2"
            shift 2
            ;;
        -g|--gain)
            GAIN="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --stream)
            STREAM="true"
            shift
            ;;
        -*)
            echo "错误: 未知选项 $1"
            show_help
            ;;
        *)
            break
            ;;
    esac
done

# 检查必要参数
if [ $# -lt 2 ]; then
    echo "错误: 必须提供文本和语音URI"
    show_help
fi

TEXT="$1"
VOICE="$2"

# 替换文本中的空格为%20
TEXT="${TEXT// /%20}"

echo "正在生成语音: '$TEXT'"
echo "使用语音: $VOICE"
echo "输出文件: $OUTPUT_FILE"

# 构建请求数据
DATA='{"model":"'"$MODEL"'","input":"'"$TEXT"'","voice":"'"$VOICE"'","response_format":"'"$RESPONSE_FORMAT"'","sample_rate":'"$SAMPLE_RATE"',"stream":'"$STREAM"',"speed":'"$SPEED"',"gain":'"$GAIN"'}'

# 发送请求并保存响应
curl --silent --request POST \
  --url https://api.siliconflow.cn/v1/audio/speech \
  --header "Authorization: Bearer $SILICONFLOW_API_KEY" \
  --header 'Content-Type: application/json' \
  --data "$DATA" \
  --output "$OUTPUT_FILE"

# 检查请求是否成功
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
    echo "语音生成成功，已保存到: $OUTPUT_FILE"
    
    # 显示文件大小
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "文件大小: $FILE_SIZE"
    exit 0
else
    echo "错误: 语音生成失败"
    # 如果文件存在但大小为0，删除它
    if [ -f "$OUTPUT_FILE" ] && [ ! -s "$OUTPUT_FILE" ]; then
        rm "$OUTPUT_FILE"
        echo "已删除空输出文件"
    fi
    exit 1
fi