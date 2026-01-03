#!/usr/bin/env python3
"""
检查 Render 服务部署状态
"""
import requests
import json
from datetime import datetime

# Render API 配置
RENDER_API_KEY = "rnd_QtPtywDxKnQAUCABtvIwBiwf0lvX"
SERVICE_ID = "srv-d5cd54a4d50c73ft2n90"
SERVICE_URL = "https://aigc-jubianage-video-generation.onrender.com"

def check_deployment():
    """检查部署状态"""
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }
    
    print("\n" + "="*60)
    print("Render 服务部署状态检查")
    print("="*60)
    
    # 1. 获取服务信息
    try:
        service_url = f"https://api.render.com/v1/services/{SERVICE_ID}"
        service_resp = requests.get(service_url, headers=headers)
        service_resp.raise_for_status()
        service_data = service_resp.json()
        
        # 处理不同的数据结构
        if 'service' in service_data:
            service = service_data['service']
        else:
            service = service_data
        
        print("\n[服务信息]")
        print(f"  服务名称: {service.get('name', 'N/A')}")
        if 'serviceDetails' in service:
            details = service['serviceDetails']
            print(f"  服务 URL: {details.get('url', 'N/A')}")
            print(f"  运行环境: {details.get('runtime', 'N/A')}")
            print(f"  计划: {details.get('plan', 'N/A')}")
        else:
            print(f"  服务 URL: {SERVICE_URL}")
    except Exception as e:
        print(f"[ERROR] 获取服务信息失败: {e}")
        # 继续检查部署状态
    
    # 2. 获取最新部署信息
    try:
        deploys_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys?limit=3"
        deploys_resp = requests.get(deploys_url, headers=headers)
        deploys_resp.raise_for_status()
        deploys_data = deploys_resp.json()
        
        # 处理不同的数据结构
        if isinstance(deploys_data, list):
            deploys_list = deploys_data
        elif "value" in deploys_data:
            deploys_list = deploys_data["value"]
        else:
            deploys_list = []
        
        if not deploys_list:
            print("\n[WARNING] 未找到部署记录")
            return False
        
        # 获取最新部署
        if "deploy" in deploys_list[0]:
            latest_deploy = deploys_list[0]["deploy"]
        else:
            latest_deploy = deploys_list[0]
        
        print("\n[最新部署]")
        print(f"  部署 ID: {latest_deploy['id']}")
        print(f"  状态: {latest_deploy['status']}")
        print(f"  提交: {latest_deploy['commit']['id'][:8]}")
        print(f"  提交信息: {latest_deploy['commit']['message'][:50]}")
        print(f"  创建时间: {latest_deploy['createdAt']}")
        print(f"  更新时间: {latest_deploy['updatedAt']}")
        
        status = latest_deploy['status']
        if status == "live":
            print("\n[SUCCESS] 服务已部署并运行！")
        elif status == "building":
            print("\n[INFO] 服务正在构建中...")
        elif status in ["update_failed", "build_failed"]:
            print("\n[ERROR] 部署失败！")
            return False
        else:
            print(f"\n[INFO] 部署状态: {status}")
    except Exception as e:
        print(f"[ERROR] 获取部署信息失败: {e}")
        return False
    
    # 3. 健康检查
    print("\n[健康检查]")
    try:
        health_resp = requests.get(f"{SERVICE_URL}/health", timeout=10)
        if health_resp.status_code == 200:
            print(f"  状态码: {health_resp.status_code}")
            print(f"  响应: {health_resp.text}")
            print("  [SUCCESS] 服务健康检查通过！")
            return True
        else:
            print(f"  状态码: {health_resp.status_code}")
            print(f"  响应: {health_resp.text}")
            return False
    except requests.exceptions.Timeout:
        print("  [WARNING] 请求超时（服务可能正在启动或休眠中）")
        print("  [INFO] 免费版服务首次请求需要约50秒唤醒")
        return False
    except requests.exceptions.ConnectionError:
        print("  [WARNING] 连接失败（服务可能未启动）")
        return False
    except Exception as e:
        print(f"  [ERROR] 健康检查失败: {e}")
        return False

if __name__ == "__main__":
    check_deployment()

