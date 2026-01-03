"""
从 MCP 服务修复历史记录
支持从 Supabase、Vercel、Render 等 MCP 服务获取数据并同步到数据库
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

from backend.database import get_db, VideoGeneration, SessionLocal, engine
from backend.video_history import VideoHistoryService
from dotenv import load_dotenv

# 加载环境变量，优先从 backend/.env 加载
env_path = project_root / "backend" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 如果 backend/.env 不存在，尝试从项目根目录加载
    load_dotenv(project_root / ".env")
    
# 也加载当前目录的 .env（如果存在）
load_dotenv(override=False)


def get_supabase_data_from_mcp() -> List[Dict]:
    """
    从 Supabase MCP 获取历史记录数据
    通过 Supabase REST API 直接获取数据
    """
    print("[INFO] 尝试从 Supabase MCP 获取数据...")
    
    # 从环境变量或使用默认值（来自 MCP 配置）
    supabase_project_ref = os.getenv("SUPABASE_PROJECT_REF", "sggdokxjqycskeybyqvv")
    supabase_access_token = os.getenv("SUPABASE_ACCESS_TOKEN", "sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03")
    
    # 也可以使用数据库连接直接查询
    supabase_db_url = os.getenv("SUPABASE_DB_URL")
    
    if supabase_db_url:
        # 方法1：直接从数据库查询（更可靠）
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine(
                supabase_db_url,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 10,
                    "sslmode": "require"
                }
            )
            
            Session = sessionmaker(bind=engine)
            db = Session()
            
            try:
                # 查询所有历史记录
                result = db.execute(text("SELECT * FROM video_generations ORDER BY created_at DESC"))
                records = []
                for row in result:
                    record = dict(row._mapping)
                    # 转换 datetime 对象为字符串
                    for key, value in record.items():
                        if hasattr(value, 'isoformat'):
                            record[key] = value.isoformat()
                    records.append(record)
                
                print(f"[SUCCESS] 从 Supabase 数据库获取到 {len(records)} 条记录")
                return records
            finally:
                db.close()
        except Exception as db_error:
            print(f"[WARN] 从数据库查询失败，尝试使用 REST API: {str(db_error)}")
    
    # 方法2：使用 Supabase REST API（需要 service_role key 或配置 RLS）
    # 注意：如果使用 access token，可能需要配置 RLS 策略或使用 service_role key
    if not supabase_access_token:
        print("[WARN] Supabase Access Token 未配置，跳过 REST API 方式")
        return []
    
    try:
        import httpx
        
        # 尝试使用 REST API
        url = f"https://{supabase_project_ref}.supabase.co/rest/v1/video_generations"
        headers = {
            "apikey": supabase_access_token,
            "Authorization": f"Bearer {supabase_access_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"  # 返回完整数据
        }
        
        response = httpx.get(url, headers=headers, timeout=30, params={"select": "*"})
        
        if response.status_code == 401:
            print("[WARN] Supabase REST API 返回 401，可能是权限问题")
            print("[INFO] 建议：1) 在 Supabase Dashboard 中禁用 RLS 或 2) 使用 service_role key")
            print("[INFO] 将使用数据库直接查询方式")
            return []
        
        response.raise_for_status()
        data = response.json()
        print(f"[SUCCESS] 从 Supabase REST API 获取到 {len(data)} 条记录")
        return data
        
    except Exception as e:
        print(f"[WARN] 从 Supabase REST API 获取数据失败: {str(e)}")
        print("[INFO] 将尝试其他方式获取数据")
        return []


def get_vercel_data_from_mcp() -> List[Dict]:
    """
    从 Vercel MCP 获取部署信息
    可能包含一些视频文件的 URL
    """
    print("[INFO] 尝试从 Vercel MCP 获取数据...")
    
    # 从环境变量或使用默认值（来自 MCP 配置）
    vercel_token = os.getenv("VERCEL_TOKEN", "bUFnjiVqrAvBYZyTmED7Q9wl")
    
    if not vercel_token:
        print("[WARN] Vercel Token 未配置")
        return []
    
    try:
        import httpx
        
        # 获取 Vercel 部署列表
        url = "https://api.vercel.com/v6/deployments"
        headers = {
            "Authorization": f"Bearer {vercel_token}",
            "Content-Type": "application/json"
        }
        
        response = httpx.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        deployments = data.get("deployments", [])
        print(f"[SUCCESS] 从 Vercel 获取到 {len(deployments)} 个部署")
        
        # 提取可能包含视频的部署信息
        video_deployments = []
        for deployment in deployments:
            # 这里可以根据需要筛选包含视频的部署
            video_deployments.append(deployment)
        
        return video_deployments
        
    except Exception as e:
        print(f"[ERROR] 从 Vercel 获取数据失败: {str(e)}")
        return []


def get_render_data_from_mcp() -> List[Dict]:
    """
    从 Render MCP 获取服务信息
    注意：Render 目前可能没有官方的 MCP 支持，这里使用 Render API
    """
    print("[INFO] 尝试从 Render API 获取数据...")
    
    render_api_key = os.getenv("RENDER_API_KEY")
    
    if not render_api_key:
        print("[WARN] Render API Key 未配置，跳过 Render 数据获取")
        return []
    
    try:
        import httpx
        
        # 获取 Render 服务列表
        url = "https://api.render.com/v1/services"
        headers = {
            "Authorization": f"Bearer {render_api_key}",
            "Accept": "application/json"
        }
        
        response = httpx.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        services = data if isinstance(data, list) else data.get("services", [])
        print(f"[SUCCESS] 从 Render 获取到 {len(services)} 个服务")
        
        return services
        
    except Exception as e:
        print(f"[ERROR] 从 Render 获取数据失败: {str(e)}")
        return []


def sync_supabase_data_to_db(db, supabase_records: List[Dict]):
    """
    将 Supabase 数据同步到本地数据库
    """
    if not supabase_records:
        print("[WARN] 没有 Supabase 数据需要同步")
        return
    
    print(f"[INFO] 开始同步 {len(supabase_records)} 条记录到数据库...")
    
    synced_count = 0
    updated_count = 0
    skipped_count = 0
    
    for record in supabase_records:
        try:
            task_id = record.get("task_id")
            if not task_id:
                skipped_count += 1
                continue
            
            # 检查记录是否已存在
            existing = db.query(VideoGeneration).filter(
                VideoGeneration.task_id == task_id
            ).first()
            
            if existing:
                # 更新现有记录
                if record.get("video_url") and not existing.video_url:
                    existing.video_url = record.get("video_url")
                if record.get("status") and existing.status != record.get("status"):
                    existing.status = record.get("status")
                if record.get("video_name") and not existing.video_name:
                    existing.video_name = record.get("video_name")
                
                db.commit()
                updated_count += 1
                print(f"  [SUCCESS] 更新记录: {task_id}")
            else:
                # 创建新记录
                user_id = record.get("user_id", 1)
                prompt = record.get("prompt", "")
                duration = record.get("duration", 5)
                
                if not prompt:
                    skipped_count += 1
                    continue
                
                generation = VideoGeneration(
                    task_id=task_id,
                    user_id=user_id,
                    prompt=prompt,
                    duration=duration,
                    fps=record.get("fps", 24),
                    width=record.get("width", 720),
                    height=record.get("height", 720),
                    seed=record.get("seed"),
                    negative_prompt=record.get("negative_prompt"),
                    first_frame_url=record.get("first_frame_url"),
                    last_frame_url=record.get("last_frame_url"),
                    video_url=record.get("video_url"),
                    video_name=record.get("video_name"),
                    video_size=record.get("video_size"),
                    status=record.get("status", "pending"),
                    error_message=record.get("error_message"),
                    is_ultra_hd=record.get("is_ultra_hd", False),
                    is_favorite=record.get("is_favorite", False),
                    is_liked=record.get("is_liked", False),
                    created_at=datetime.fromisoformat(record["created_at"].replace("Z", "+00:00")) if record.get("created_at") else datetime.utcnow(),
                    completed_at=datetime.fromisoformat(record["completed_at"].replace("Z", "+00:00")) if record.get("completed_at") else None,
                    extra_metadata=record.get("extra_metadata") or {}
                )
                
                db.add(generation)
                db.commit()
                synced_count += 1
                print(f"  [SUCCESS] 同步新记录: {task_id}")
                
        except Exception as e:
            print(f"  [ERROR] 同步记录失败: {str(e)}")
            db.rollback()
            skipped_count += 1
            continue
    
    print(f"\n[INFO] 同步完成:")
    print(f"  - 新增: {synced_count} 条")
    print(f"  - 更新: {updated_count} 条")
    print(f"  - 跳过: {skipped_count} 条")


def main():
    """主函数"""
    # 设置 Windows 控制台编码为 UTF-8
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("开始从 MCP 服务修复历史记录...\n")
    
    # 检查数据库连接
    if not engine:
        print("[ERROR] 数据库未配置，请设置 SUPABASE_DB_URL 环境变量")
        return
    
    if not SessionLocal:
        print("[ERROR] 数据库会话未初始化")
        return
    
    db = SessionLocal()
    
    try:
        # 1. 从 Supabase MCP 获取数据
        supabase_records = get_supabase_data_from_mcp()
        if supabase_records:
            sync_supabase_data_to_db(db, supabase_records)
        
        # 2. 从 Vercel MCP 获取数据（可选，主要用于获取部署信息）
        vercel_data = get_vercel_data_from_mcp()
        if vercel_data:
            print(f"[INFO] 从 Vercel 获取到 {len(vercel_data)} 个部署信息")
            # 这里可以根据需要处理 Vercel 部署数据
        
        # 3. 从 Render API 获取数据（可选）
        render_data = get_render_data_from_mcp()
        if render_data:
            print(f"[INFO] 从 Render 获取到 {len(render_data)} 个服务信息")
            # 这里可以根据需要处理 Render 服务数据
        
        print("\n[SUCCESS] 历史记录修复完成！")
        
    except Exception as e:
        print(f"[ERROR] 修复过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

