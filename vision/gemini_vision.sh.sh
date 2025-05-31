#!/bin/bash

# --- 配置 ---
# 1. 将你的 Google API Key 粘贴到引号内
# 2. 或者，脚本会尝试从环境变量 GOOGLE_API_KEY 读取
# 3. 如果上面两者都没有，脚本会提示你输入
API_KEY="AIzaSyDHXN8YZGfuqIuz8SkXOniOx019tYWHbMs"

# 模型名称
MODEL_NAME="gemini-2.0-flash"

# --- 函数 ---
function show_usage() {
  echo "使用方法: $0 <图片路径> [\"你的提问\"]"
  echo "例如: $0 ./my_image.jpg \"这张图片里有什么动物？\""
  echo "如果未提供提问，将使用默认提问：\"详细描述这张图片。\""
  exit 1
}

function get_mime_type() {
  local file_path="$1"
  local extension="${file_path##*.}"
  extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]') # 转小写

  case "$extension" in
    jpg|jpeg) echo "image/jpeg" ;;
    png) echo "image/png" ;;
    webp) echo "image/webp" ;;
    # heic|heif) echo "image/heic" ;; # Gemini 可能支持，但 base64 和 curl 行为可能需额外注意
    *)
      echo "错误: 不支持的图片格式 '$extension'. 请使用 jpg, png, or webp." >&2
      exit 1
      ;;
  esac
}

# --- 主逻辑 ---

# 检查参数数量
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  show_usage
fi

IMAGE_PATH="$1"
PROMPT_TEXT="${2:-详细描述这张图片。}" # 如果第二个参数未提供，使用默认提问

# 检查图片文件是否存在
if [ ! -f "$IMAGE_PATH" ]; then
  echo "错误: 图片文件未找到 '$IMAGE_PATH'" >&2
  exit 1
fi

# 获取或提示输入 API Key
if [ -z "$API_KEY" ]; then
  if [ -n "$GOOGLE_API_KEY" ]; then
    API_KEY="$GOOGLE_API_KEY"
    echo "从环境变量 GOOGLE_API_KEY 中读取 API 密钥。"
  else
    read -sp "请输入你的 Google API Key: " API_KEY_INPUT
    echo # 换行
    if [ -z "$API_KEY_INPUT" ]; then
      echo "错误: API Key 未提供。" >&2
      exit 1
    fi
    API_KEY="$API_KEY_INPUT"
  fi
fi

# 获取图片MIME类型
MIME_TYPE=$(get_mime_type "$IMAGE_PATH")

# 将图片转换为Base64
echo "正在将图片编码为 Base64..."
# 检测操作系统并使用相应的 base64 命令参数
if [[ "$(uname)" == "Darwin" ]]; then
  # macOS 系统
  IMAGE_BASE64=$(base64 -i "$IMAGE_PATH")
else
  # Linux 系统
  IMAGE_BASE64=$(base64 -w 0 "$IMAGE_PATH") # -w 0 避免换行
fi

if [ $? -ne 0 ]; then
  echo "错误: 无法将图片编码为 Base64。" >&2
  exit 1
fi
echo "图片编码完成。"

# 构建JSON请求体
# 使用 cat 和 EOF 来构建多行JSON，确保变量被正确替换
REQUEST_BODY=$(cat <<EOF
{
  "contents": [{
    "parts": [
      {"text": "$PROMPT_TEXT"},
      {"inline_data": {
        "mime_type": "$MIME_TYPE",
        "data": "$IMAGE_BASE64"
      }}
    ]
  }],
  "generationConfig": {
    "temperature": 0.4,
    "topK": 32,
    "topP": 1,
    "maxOutputTokens": 4096
  }
}
EOF
)

API_URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${API_KEY}"

echo "正在向 Gemini API 发送请求..."
# 使用 curl 发送请求
# -s: silent模式
# -X POST: HTTP POST 请求
# -H: Header
# -d: data (请求体)
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY" \
  "$API_URL")

# 检查curl是否成功执行
if [ $? -ne 0 ]; then
  echo "错误: curl 命令执行失败。" >&2
  echo "响应内容: $RESPONSE" >&2 # 输出原始响应以便调试
  exit 1
fi

# 检查jq是否安装，并尝试解析响应
if command -v jq &> /dev/null; then
  # 检查API是否返回错误
  API_ERROR_MESSAGE=$(echo "$RESPONSE" | jq -r '.error.message // empty')
  if [ -n "$API_ERROR_MESSAGE" ]; then
    echo "Gemini API 错误: $API_ERROR_MESSAGE" >&2
    echo "完整响应:" >&2
    echo "$RESPONSE" | jq . >&2
    exit 1
  fi

  # 提取生成的文本
  GENERATED_TEXT=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].text // empty')

  if [ -z "$GENERATED_TEXT" ]; then
      echo "未能从API响应中提取文本，或响应结构不符合预期。" >&2
      echo "原始响应:" >&2
      echo "$RESPONSE" | jq . >&2
      exit 1
  fi

  echo "----------------------------------------"
  echo "Gemini 的回答:"
  echo "$GENERATED_TEXT"
  echo "----------------------------------------"
else
  echo "警告: jq 未安装。无法美化和精确解析JSON响应。" >&2
  echo "原始响应:" >&2
  echo "$RESPONSE"
  echo "建议安装 jq (brew install jq) 以获得更好的输出。" >&2
fi

exit 0