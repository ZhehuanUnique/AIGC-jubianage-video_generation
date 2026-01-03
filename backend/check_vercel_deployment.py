#!/usr/bin/env python3
"""
检查 Vercel 部署状态
"""
import requests
import json

# Vercel API 配置（通过环境变量或直接使用）
VERCEL_TOKEN = "bUFnjiVqrAvBYZyTmED7Q9wl"
PROJECT_ID = "aigc-jubianage-video-generation"
FRONTEND_URL = "https://aigc-jubianage-video-generation.vercel.app"
BACKEND_URL = "https://aigc-jubianage-video-generation.onrender.com"

def check_vercel_deployment():
    """检查 Vercel 部署状态"""
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}"
    }
    
    print("\n" + "="*60)
    print("Vercel 部署状态检查")
    print("="*60)
    
    # 1. 检查项目信息
    try:
        project_url = f"https://api.vercel.com/v9/projects/{PROJECT_ID}"
        project_resp = requests.get(project_url, headers=headers)
        project_resp.raise_for_status()
        project_data = project_resp.json()
        
        print("\n[项目信息]")
        print(f"  项目名称: {project_data.get('name', 'N/A')}")
        print(f"  框架: {project_data.get('framework', 'N/A')}")
        print(f"  根目录: {project_data.get('rootDirectory', 'N/A')}")
    except Exception as e:
        print(f"[ERROR] 获取项目信息失败: {e}")
        return False
    
    # 2. 检查环境变量
    try:
        env_url = f"https://api.vercel.com/v9/projects/{PROJECT_ID}/env"
        env_resp = requests.get(env_url, headers=headers)
        env_resp.raise_for_status()
        env_data = env_resp.json()
        
        print("\n[环境变量]")
        backend_url_found = False
        for env in env_data.get("envs", []):
            if env.get("key") == "BACKEND_URL":
                value = env.get("value", "")
                print(f"  BACKEND_URL = {value}")
                if value == BACKEND_URL:
                    print("  [SUCCESS] BACKEND_URL 已正确配置！")
                    backend_url_found = True
                else:
                    print(f"  [WARNING] BACKEND_URL 值不正确，期望: {BACKEND_URL}")
        if not backend_url_found:
            print("  [ERROR] 未找到 BACKEND_URL 环境变量")
    except Exception as e:
        print(f"[ERROR] 获取环境变量失败: {e}")
    
    # 3. 检查最新部署
    try:
        deployments_url = f"https://api.vercel.com/v6/deployments?projectId={PROJECT_ID}&limit=1"
        deploy_resp = requests.get(deployments_url, headers=headers)
        deploy_resp.raise_for_status()
        deploy_data = deploy_resp.json()
        
        if deploy_data.get("deployments"):
            latest = deploy_data["deployments"][0]
            print("\n[最新部署]")
            print(f"  部署 ID: {latest.get('uid', 'N/A')}")
            print(f"  状态: {latest.get('readyState', 'N/A')}")
            print(f"  目标: {latest.get('target', 'N/A')}")
            print(f"  创建时间: {latest.get('createdAt', 'N/A')}")
            
            ready_state = latest.get('readyState', '')
            if ready_state == "READY":
                print("  [SUCCESS] 部署已完成并运行！")
            elif ready_state == "BUILDING":
                print("  [INFO] 部署正在构建中...")
            elif ready_state == "ERROR":
                print("  [ERROR] 部署失败！")
            else:
                print(f"  [INFO] 部署状态: {ready_state}")
    except Exception as e:
        print(f"[ERROR] 获取部署信息失败: {e}")
    
    # 4. 检查前端访问
    print("\n[前端访问测试]")
    try:
        frontend_resp = requests.get(FRONTEND_URL, timeout=10)
        if frontend_resp.status_code == 200:
            print(f"  状态码: {frontend_resp.status_code}")
            print("  [SUCCESS] 前端可正常访问！")
        else:
            print(f"  状态码: {frontend_resp.status_code}")
    except Exception as e:
        print(f"  [ERROR] 前端访问失败: {e}")
    
    # 5. 检查后端访问
    print("\n[后端访问测试]")
    try:
        backend_resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if backend_resp.status_code == 200:
            print(f"  状态码: {backend_resp.status_code}")
            print(f"  响应: {backend_resp.text}")
            print("  [SUCCESS] 后端可正常访问！")
        else:
            print(f"  状态码: {backend_resp.status_code}")
    except requests.exceptions.Timeout:
        print("  [WARNING] 请求超时（后端可能正在启动）")
    except Exception as e:
        print(f"  [ERROR] 后端访问失败: {e}")
    
    print("\n" + "="*60)
    print("检查完成")
    print("="*60)

if __name__ == "__main__":
    check_vercel_deployment()

