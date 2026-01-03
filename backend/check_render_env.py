#!/usr/bin/env python3
"""
检查 Render 环境变量配置
"""
import os
import requests
import json
from pathlib import Path

# Render API 配置
RENDER_API_KEY = "rnd_QtPtywDxKnQAUCABtvIwBiwf0lvX"
SERVICE_ID = "srv-d5cd54a4d50c73ft2n90"

# 必需的环境变量
REQUIRED_VARS = [
    "VOLCENGINE_ACCESS_KEY_ID",
    "VOLCENGINE_SECRET_ACCESS_KEY",
    "COS_SECRET_ID",
    "COS_SECRET_KEY"
]

# 占位符值（需要替换的）
PLACEHOLDERS = [
    "your_access_key_id",
    "your_secret_access_key",
    "your_secret_id",
    "your_secret_key"
]

def check_env_vars():
    """检查环境变量配置"""
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }
    
    # 获取环境变量
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[ERROR] 获取环境变量失败: {e}")
        return False
    
    # 解析环境变量
    env_vars = {}
    # API 返回的可能是列表格式
    if isinstance(data, list):
        items = data
    else:
        items = data.get("envVars", [])
    
    for item in items:
        if "envVar" in item:
            key = item["envVar"]["key"]
            value = item["envVar"]["value"]
        else:
            key = item.get("key", "")
            value = item.get("value", "")
        if key:
            env_vars[key] = value
    
    # 检查必需的环境变量
    print("\n" + "="*50)
    print("必需环境变量检查")
    print("="*50)
    
    all_ok = True
    results = []
    
    for key in REQUIRED_VARS:
        if key not in env_vars:
            print(f"[X] {key}: 未找到")
            results.append({"key": key, "status": "missing", "value": None})
            all_ok = False
        else:
            value = env_vars[key]
            # 检查是否是占位符
            is_placeholder = any(ph in value.lower() for ph in PLACEHOLDERS) or value.startswith("your_")
            
            if is_placeholder:
                print(f"[X] {key}: 仍是占位符值 ({value[:30]}...)")
                results.append({"key": key, "status": "placeholder", "value": value})
                all_ok = False
            else:
                # 显示前20个字符
                preview = value[:20] + "..." if len(value) > 20 else value
                print(f"[OK] {key}: 已更新 ({preview})")
                results.append({"key": key, "status": "ok", "value": preview})
    
    print("\n" + "="*50)
    if all_ok:
        print("[SUCCESS] 所有必需的环境变量已正确配置！")
        return True
    else:
        print("[WARNING] 仍有环境变量需要更新")
        return False

if __name__ == "__main__":
    check_env_vars()

