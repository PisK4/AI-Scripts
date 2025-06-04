import requests
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件中的环境变量
dotenv_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
load_dotenv(dotenv_path=dotenv_path)

# 从环境变量获取API密钥
api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    raise ValueError("SILICONFLOW_API_KEY环境变量未设置，请在.env文件中配置")

# 获取voices.json文件路径
siliconflow_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
voices_json_path = os.path.join(siliconflow_dir, "voices.json")

# 检查文件是否存在
if not os.path.exists(voices_json_path):
    raise FileNotFoundError(f"找不到音色列表文件: {voices_json_path}")

# 读取voices.json文件
try:
    with open(voices_json_path, "r", encoding="utf-8") as f:
        voices_data = json.load(f)
except json.JSONDecodeError:
    raise ValueError(f"无法解析 {voices_json_path}，文件格式不正确")

# 检查JSON格式是否符合预期
if not isinstance(voices_data, dict) or "result" not in voices_data:
    print(f"警告：{voices_json_path} 格式可能不正确，尝试继续处理...")
    # 如果格式不正确，尝试直接使用整个JSON作为列表
    voice_list = voices_data if isinstance(voices_data, list) else []
else:
    # 正常情况下从"result"字段获取音色列表
    voice_list = voices_data["result"]

# 检查列表是否为空
if not voice_list:
    print("音色列表为空，没有音色需要删除")
    exit(0)

print(f"共找到 {len(voice_list)} 个音色需要删除")
print("=" * 50)

# 询问用户确认
confirm = input(f"确认要删除所有 {len(voice_list)} 个音色吗？(y/n): ").strip().lower()
if confirm != 'y':
    print("操作已取消")
    exit(0)

# 删除音色的URL和请求头
url = "https://api.siliconflow.cn/v1/audio/voice/deletions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 记录成功和失败的删除
successful = 0
failed = 0
failed_voices = []

# 循环删除每个音色
for i, voice in enumerate(voice_list, 1):
    # 检查voice是否有uri字段
    if "uri" not in voice:
        print(f"[{i}/{len(voice_list)}] 跳过：缺少URI字段")
        failed += 1
        continue
    
    voice_uri = voice["uri"]
    voice_name = voice.get("customName", "未命名")
    
    print(f"[{i}/{len(voice_list)}] 正在删除音色: {voice_name} (URI: {voice_uri})")
    
    # 准备请求数据
    data = {
        "uri": voice_uri
    }
    
    try:
        # 发送删除请求
        response = requests.post(url, json=data, headers=headers)
        
        # 检查响应状态
        if response.status_code == 200:
            print(f"  ✅ 删除成功: {voice_name}")
            successful += 1
        else:
            print(f"  ❌ 删除失败，状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            failed += 1
            failed_voices.append(voice_name)
        
        # 短暂暂停，避免API限流
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ❌ 删除时发生错误: {e}")
        failed += 1
        failed_voices.append(voice_name)
        # 错误后暂停时间稍长
        time.sleep(1)

print("=" * 50)
print(f"删除完成：成功 {successful} 个，失败 {failed} 个")

# 如果有失败的音色，显示详情
if failed > 0:
    print("删除失败的音色:")
    for voice_name in failed_voices:
        print(f"- {voice_name}")

# 如果全部删除成功，且数量大于0，则删除voices.json文件
if successful > 0 and failed == 0:
    try:
        # 先备份原文件
        backup_path = voices_json_path + ".bak"
        os.rename(voices_json_path, backup_path)
        print(f"所有音色已成功删除，原音色列表已备份到: {backup_path}")
        
        # 创建一个新的空的音色列表文件
        with open(voices_json_path, "w", encoding="utf-8") as f:
            json.dump({"result": []}, f, indent=2, ensure_ascii=False)
        print(f"已创建新的空音色列表文件: {voices_json_path}")
    except Exception as e:
        print(f"处理文件时出错: {e}")
