import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件中的环境变量
dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
load_dotenv(dotenv_path=dotenv_path)

# 从环境变量获取API密钥
api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    raise ValueError("SILICONFLOW_API_KEY环境变量未设置，请在.env文件中配置")

# 设置删除音色的URI参数
voice_uri = input("请输入要删除的音色URI (格式: speech:your-voice-name:xxx:xxxx): ")
if not voice_uri or not voice_uri.startswith("speech:"):
    raise ValueError("音色URI格式不正确，应为: speech:your-voice-name:xxx:xxxx")

url = "https://api.siliconflow.cn/v1/audio/voice/deletions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "uri": voice_uri
}

# 发送删除请求
response = requests.post(url, json=data, headers=headers)

# 检查响应状态
if response.status_code == 200:
    print(f"音色删除成功: {voice_uri}")
    print(f"响应内容: {response.json()}")
else:
    print(f"删除失败，状态码: {response.status_code}")
    print(f"错误信息: {response.text}")
