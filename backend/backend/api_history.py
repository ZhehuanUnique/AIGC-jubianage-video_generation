"""
视频生成历史记录 API
新增的 API 端点，用于查询和管理视频生成历史
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .database import get_db, VideoGeneration
from .video_history import VideoHistoryService
from .auth import AuthService
from .video_processing import VideoProcessingService

router = APIRouter(prefix="/api/v1/video", tags=["video-history"])


class VideoGenerationHistoryItem(BaseModel):
    """视频生成历史记录项"""
    id: int
    task_id: str
    prompt: str
    duration: int
    fps: int
    width: int
    height: int
    status: str
    video_url: Optional[str] = None
    video_name: Optional[str] = None
    first_frame_url: Optional[str] = None
    last_frame_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    is_ultra_hd: Optional[bool] = False
    is_favorite: Optional[bool] = False
    is_liked: Optional[bool] = False
    
    class Config:
        from_attributes = True


class VideoGenerationHistoryResponse(BaseModel):
    """视频生成历史响应"""
    total: int
    items: List[VideoGenerationHistoryItem]
    limit: int
    offset: int


def get_current_user_id(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Optional[Session] = None
) -> int:
    """获取当前用户ID（通过 API Key 或默认用户）"""
    try:
        # 如果数据库未配置，返回默认用户ID（1）
        if not db:
            return 1
        
        if x_api_key:
            user = AuthService.get_user_by_api_key(db, x_api_key)
            if user:
                return user.id
        
        # 如果没有提供 API Key 或无效，使用默认用户
        default_user = AuthService.get_or_create_default_user(db)
        return default_user.id
    except HTTPException:
        raise
    except Exception as e:
        # 如果数据库不可用，返回默认用户ID（1）而不是抛出异常
        print(f"获取用户ID失败，使用默认用户: {str(e)}")
        return 1


@router.get("/history", response_model=VideoGenerationHistoryResponse)
async def get_video_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(pending|processing|completed|failed)$"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    获取视频生成历史记录
    
    - **limit**: 每页数量（1-100）
    - **offset**: 偏移量
    - **status**: 筛选状态（pending/processing/completed/failed）
    - **x_api_key**: API Key（可选，用于多用户模式）
    """
    try:
        # 尝试获取数据库连接
        try:
            from .database import get_db
            db_gen = get_db()
            db = next(db_gen)
        except Exception as db_error:
            # 数据库未配置，返回空列表
            print(f"数据库未配置，返回空历史记录: {str(db_error)}")
            db = None
        
        # 获取用户ID（如果数据库不可用，返回默认用户ID）
        try:
            user_id = get_current_user_id(x_api_key, db)
        except Exception as db_init_error:
            # 数据库未初始化或表不存在，返回空列表
            print(f"数据库初始化错误: {str(db_init_error)}")
            return VideoGenerationHistoryResponse(
                total=0,
                items=[],
                limit=limit,
                offset=offset
            )
        
        # 在获取历史记录前，先清理超时的任务
        try:
            cleaned_count = VideoHistoryService.cleanup_timeout_tasks(db, timeout_minutes=5)
            if cleaned_count > 0:
                print(f"✅ 已清理 {cleaned_count} 个超时任务")
        except Exception as cleanup_error:
            # 清理失败不影响历史记录查询
            print(f"清理超时任务失败: {str(cleanup_error)}")
        
        # 获取历史记录
        try:
            generations = VideoHistoryService.get_user_generations(
                db, user_id, limit=limit, offset=offset, status=status
            )
            
            # 获取总数
            total = VideoHistoryService.get_user_generation_count(db, user_id, status=status)
        except Exception as query_error:
            # 查询失败，可能是表不存在，返回空列表
            print(f"查询历史记录失败: {str(query_error)}")
            return VideoGenerationHistoryResponse(
                total=0,
                items=[],
                limit=limit,
                offset=offset
            )
        
        # 转换为响应模型
        items = [
            VideoGenerationHistoryItem(
                id=gen.id,
                task_id=gen.task_id,
                prompt=gen.prompt,
                duration=gen.duration,
                fps=gen.fps,
                width=gen.width,
                height=gen.height,
                status=gen.status,
                video_url=gen.video_url,
                video_name=gen.video_name,
                first_frame_url=getattr(gen, 'first_frame_url', None),
                last_frame_url=getattr(gen, 'last_frame_url', None),
                created_at=gen.created_at,
                completed_at=gen.completed_at,
                is_ultra_hd=getattr(gen, 'is_ultra_hd', False),
                is_favorite=getattr(gen, 'is_favorite', False),
                is_liked=getattr(gen, 'is_liked', False)
            )
            for gen in generations
        ]
        
        return VideoGenerationHistoryResponse(
            total=total,
            items=items,
            limit=limit,
            offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        # 其他错误，返回空列表而不是抛出异常
        print(f"获取历史记录异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return VideoGenerationHistoryResponse(
            total=0,
            items=[],
            limit=limit,
            offset=offset
        )
    finally:
        # 确保关闭数据库连接
        if 'db' in locals() and db:
            try:
                db.close()
            except:
                pass


@router.get("/history/{task_id}")
async def get_video_by_task_id(
    task_id: str,
    x_api_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """根据任务ID获取视频生成记录"""
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = VideoHistoryService.get_generation_by_task_id(db, task_id)
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        # 检查权限（只能查看自己的记录）
        if generation.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此记录")
        
        return VideoGenerationHistoryItem(
            id=generation.id,
            task_id=generation.task_id,
            prompt=generation.prompt,
            duration=generation.duration,
            fps=generation.fps,
            width=generation.width,
            height=generation.height,
            status=generation.status,
            video_url=generation.video_url,
            video_name=generation.video_name,
            first_frame_url=getattr(generation, 'first_frame_url', None),
            last_frame_url=getattr(generation, 'last_frame_url', None),
            created_at=generation.created_at,
            completed_at=generation.completed_at,
            is_ultra_hd=getattr(generation, 'is_ultra_hd', False),
            is_favorite=getattr(generation, 'is_favorite', False),
            is_liked=getattr(generation, 'is_liked', False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频记录失败: {str(e)}")


@router.delete("/history/{generation_id}")
async def delete_video_history(
    generation_id: int,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """删除视频生成记录"""
    try:
        # 获取用户ID
        try:
            user_id = get_current_user_id(x_api_key, db)
            print(f"删除视频请求: generation_id={generation_id}, user_id={user_id}")
        except Exception as user_error:
            print(f"获取用户ID失败: {str(user_error)}")
            raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(user_error)}")
        
        # 先检查记录是否存在
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id
        ).first()
        
        if not generation:
            print(f"视频记录不存在: generation_id={generation_id}")
            raise HTTPException(status_code=404, detail=f"视频记录不存在 (ID: {generation_id})")
        
        # 检查权限
        if generation.user_id != user_id:
            print(f"权限不足: generation_id={generation_id}, generation.user_id={generation.user_id}, current_user_id={user_id}")
            raise HTTPException(status_code=403, detail="无权删除此视频记录")
        
        # 执行删除
        try:
            success = VideoHistoryService.delete_generation(db, generation_id, user_id)
            
            if not success:
                print(f"删除失败: generation_id={generation_id}, user_id={user_id}")
                raise HTTPException(status_code=404, detail="视频记录不存在或无权删除")
            
            print(f"删除成功: generation_id={generation_id}, user_id={user_id}")
            return {"success": True, "message": "删除成功"}
        except HTTPException:
            raise
        except Exception as delete_error:
            print(f"删除操作失败: {str(delete_error)}")
            raise HTTPException(status_code=500, detail=f"删除操作失败: {str(delete_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除视频异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        # 确保关闭数据库连接
        if 'db' in locals() and db:
            try:
                db.close()
            except:
                pass


@router.patch("/history/{generation_id}/favorite")
async def toggle_favorite(
    generation_id: int,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """切换收藏状态"""
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id,
            VideoGeneration.user_id == user_id
        ).first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        generation.is_favorite = not generation.is_favorite
        db.commit()
        
        return {"success": True, "is_favorite": generation.is_favorite}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.patch("/history/{generation_id}/like")
async def toggle_like(
    generation_id: int,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """切换点赞状态"""
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id,
            VideoGeneration.user_id == user_id
        ).first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        generation.is_liked = not generation.is_liked
        db.commit()
        
        return {"success": True, "is_liked": generation.is_liked}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.patch("/history/{generation_id}/ultra-hd")
async def toggle_ultra_hd(
    generation_id: int,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """切换超清标记"""
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id,
            VideoGeneration.user_id == user_id
        ).first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        generation.is_ultra_hd = not generation.is_ultra_hd
        db.commit()
        
        return {"success": True, "is_ultra_hd": generation.is_ultra_hd}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


# ========== 视频增强 API ==========

class EnhanceResolutionRequest(BaseModel):
    """提升分辨率请求"""
    method: str = "real_esrgan"  # "real_esrgan" 或 "waifu2x"
    scale: int = 2  # 放大倍数（2 = 2倍，1080P -> 4K）


class EnhanceFPSRequest(BaseModel):
    """提升帧率请求"""
    target_fps: int = 60
    method: str = "rife"  # "rife" 或 "film"
    auto_switch: bool = True  # 是否自动检测大运动并切换


@router.post("/history/{generation_id}/enhance-resolution")
async def enhance_resolution(
    generation_id: int,
    request: EnhanceResolutionRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    提升视频分辨率（超分辨率）
    
    支持的方法：
    - real_esrgan: Real-ESRGAN（默认）
    - waifu2x: Waifu2x
    """
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id,
            VideoGeneration.user_id == user_id
        ).first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        if not generation.video_url:
            raise HTTPException(status_code=400, detail="视频URL不存在")
        
        if generation.status != "completed":
            raise HTTPException(status_code=400, detail="视频尚未生成完成")
        
        # 调用视频处理服务
        processing_service = VideoProcessingService()
        result = await processing_service.enhance_resolution(
            video_url=generation.video_url,
            method=request.method,
            scale=request.scale
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"分辨率提升失败: {result.get('error', '未知错误')}"
            )
        
        # 更新视频URL和分辨率
        generation.video_url = result["output_url"]
        generation.width = result["enhanced_resolution"][0]
        generation.height = result["enhanced_resolution"][1]
        generation.is_ultra_hd = True
        
        # 更新元数据
        if not generation.extra_metadata:
            generation.extra_metadata = {}
        generation.extra_metadata["enhanced_resolution"] = {
            "method": result["method"],
            "original": result["original_resolution"],
            "enhanced": result["enhanced_resolution"],
            "processing_time": result["processing_time"]
        }
        
        db.commit()
        
        return {
            "success": True,
            "message": "分辨率提升成功",
            "output_url": result["output_url"],
            "original_resolution": result["original_resolution"],
            "enhanced_resolution": result["enhanced_resolution"],
            "method": result["method"],
            "processing_time": result["processing_time"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分辨率提升失败: {str(e)}")


@router.post("/history/{generation_id}/enhance-fps")
async def enhance_fps(
    generation_id: int,
    request: EnhanceFPSRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """
    提升视频帧率（插帧）
    
    支持的方法：
    - rife: RIFE（默认，快速）
    - film: FILM（适合大运动/高遮挡，较慢）
    
    如果启用 auto_switch，系统会自动检测大运动并切换到 FILM
    """
    try:
        user_id = get_current_user_id(x_api_key, db)
        
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id,
            VideoGeneration.user_id == user_id
        ).first()
        
        if not generation:
            raise HTTPException(status_code=404, detail="视频记录不存在")
        
        if not generation.video_url:
            raise HTTPException(status_code=400, detail="视频URL不存在")
        
        if generation.status != "completed":
            raise HTTPException(status_code=400, detail="视频尚未生成完成")
        
        # 如果切换到 FILM，给出提示
        if request.method == "film" or (request.auto_switch and request.method == "rife"):
            # 提示会在前端显示
            pass
        
        # 调用视频处理服务
        processing_service = VideoProcessingService()
        result = await processing_service.enhance_fps(
            video_url=generation.video_url,
            target_fps=request.target_fps,
            method=request.method,
            auto_switch=request.auto_switch
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"帧率提升失败: {result.get('error', '未知错误')}"
            )
        
        # 更新视频URL和帧率
        generation.video_url = result["output_url"]
        generation.fps = result["enhanced_fps"]
        
        # 更新元数据
        if not generation.extra_metadata:
            generation.extra_metadata = {}
        generation.extra_metadata["enhanced_fps"] = {
            "method": result["method"],
            "original_fps": result["original_fps"],
            "enhanced_fps": result["enhanced_fps"],
            "auto_switched": result.get("auto_switched", False),
            "processing_time": result["processing_time"]
        }
        
        db.commit()
        
        return {
            "success": True,
            "message": "帧率提升成功",
            "output_url": result["output_url"],
            "original_fps": result["original_fps"],
            "enhanced_fps": result["enhanced_fps"],
            "method": result["method"],
            "auto_switched": result.get("auto_switched", False),
            "processing_time": result["processing_time"],
            "warning": "使用 FILM 处理时间较长，请耐心等待" if result["method"] == "film" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"帧率提升失败: {str(e)}")

