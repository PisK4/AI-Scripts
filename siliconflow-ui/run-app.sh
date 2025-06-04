#!/bin/bash

# SiliconFlow UI 应用启动脚本
# 此脚本用于启动SiliconFlow语音工具集的Web界面

# 获取脚本所在目录的绝对路径（无论从哪里调用脚本）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置彩色输出
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}正在启动 SiliconFlow 语音工具集...${NC}"

# 检查虚拟环境是否存在
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在为您创建...${NC}"
    
    # 检查 python 是否安装
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 Python3。请先安装 Python3 再运行此脚本。${NC}"
        exit 1
    fi
    
    # 创建虚拟环境
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 创建虚拟环境失败。请检查您的 Python 安装。${NC}"
        exit 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo -e "${BLUE}正在安装依赖项...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 安装依赖失败。请查看上面的错误信息。${NC}"
        exit 1
    fi
else
    # 激活虚拟环境
    source venv/bin/activate
fi

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}提示: 未找到 .env 文件。${NC}"
    
    if [ -f "env_template.txt" ]; then
        echo -e "${BLUE}正在从模板创建 .env 文件...${NC}"
        cp env_template.txt .env
        echo -e "${YELLOW}请编辑 .env 文件，填入您的 API 密钥。${NC}"
    else
        echo -e "${YELLOW}请创建 .env 文件并添加您的 API 密钥:${NC}"
        echo -e "${YELLOW}SILICONFLOW_API_KEY=您的API密钥${NC}"
    fi
fi

# 信号处理函数
function handle_signal() {
    echo -e "\n${BLUE}收到中断信号，正在优雅地关闭应用...${NC}"
    exit 130  # 130是SIGINT的标准退出码
}

# 注册信号处理函数
trap handle_signal SIGINT SIGTERM

# 运行应用
echo -e "${GREEN}启动 SiliconFlow 语音工具集界面...${NC}"

# 使用exec启动Python程序，这样信号会直接传递给Python进程
exec python run_app.py

# 下面的代码只有在exec失败时才会执行
exec_status=$?
echo -e "${RED}应用启动失败，退出代码: $exec_status${NC}"
echo -e "${YELLOW}如有问题，请检查日志或联系技术支持。${NC}"
exit $exec_status
