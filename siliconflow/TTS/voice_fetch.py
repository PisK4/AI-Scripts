import requests
import json
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

url = "https://api.siliconflow.cn/v1/audio/voice/list"

headers = {"Authorization": f"Bearer {api_key}"}

response = requests.request("GET", url, headers=headers)

# 获取siliconflow目录路径
siliconflow_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 保存json到siliconflow目录
voices_json_path = os.path.join(siliconflow_dir, "voices.json")
with open(voices_json_path, "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=2, ensure_ascii=False)

# 获取音色列表成功
print(f"获取音色列表成功, 保存到 {voices_json_path}")
