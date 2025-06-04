#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow语音工具集 - 应用启动脚本
此脚本用于启动SiliconFlow语音工具集Web应用程序
"""

import os
import sys
import signal
import subprocess
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 将项目根目录添加到系统路径
sys.path.append(str(ROOT_DIR))

# 全局进程变量
streamlit_process = None

# 信号处理函数
def signal_handler(sig, frame):
    """
    处理中断信号(Ctrl+C)，强制关闭应用
    """
    print("\n正在强制关闭应用...")
    if streamlit_process:
        try:
            import os
            import signal as sig
            import psutil
            
            # 获取streamlit主进程
            parent = psutil.Process(streamlit_process.pid)
            
            # 获取所有子进程
            children = parent.children(recursive=True)
            
            # 首先尝试正常终止
            print("正在终止Streamlit服务...")
            streamlit_process.terminate()
            
            # 给一个短暂停让进程自行终止
            try:
                streamlit_process.wait(timeout=2)
                print("成功终止Streamlit主进程")
            except subprocess.TimeoutExpired:
                # 如果超时，则强制终止
                print("强制终止Streamlit主进程...")
                streamlit_process.kill()
            
            # 强制关闭所有子进程
            for child in children:
                try:
                    print(f"结束子进程: {child.pid}")
                    os.kill(child.pid, sig.SIGKILL)
                except (psutil.NoSuchProcess, ProcessLookupError):
                    pass
        except ImportError:
            # 如果没有psutil，则直接强制终止主进程
            print("强制终止Streamlit进程...")
            streamlit_process.kill()
        except Exception as e:
            print(f"终止进程时出错: {e}")
            # 最后手段，强制终止
            try:
                streamlit_process.kill()
            except:
                pass
    
    print("应用已安全关闭。")
    # 强制退出脚本
    os._exit(0)

# 主函数
def main():
    """
    启动SiliconFlow语音工具集Web应用程序
    优雅地处理中断信号
    """
    global streamlit_process
    
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("正在启动SiliconFlow语音工具集...")
    
    # 检查是否存在.env文件
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        print("\n警告: 未找到.env文件，应用可能无法正常工作")
        print("请创建.env文件，并添加您的SiliconFlow API密钥:")
        print("SILICONFLOW_API_KEY=您的API密钥\n")
    
    try:
        # 启动新的多页面Streamlit应用，使用Popen而不是run，这样可以控制进程
        os.chdir(str(ROOT_DIR))
        streamlit_process = subprocess.Popen(["streamlit", "run", "Home.py"])
        
        # 保持主进程运行，直到streamlit进程结束
        streamlit_process.wait()
    except Exception as e:
        print(f"应用启动失败: {e}")
    except KeyboardInterrupt:
        # 这里应该不会进入，因为我们已经设置了信号处理器
        signal_handler(signal.SIGINT, None)

# 执行主函数
if __name__ == "__main__":
    main()
