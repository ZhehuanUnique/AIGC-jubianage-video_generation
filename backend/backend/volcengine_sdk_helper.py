"""
使用火山引擎官方 SDK 的辅助函数
参考：https://github.com/volcengine/volc-sdk-python
"""
from volcengine.visual.VisualService import VisualService
from typing import Dict, Any, Optional
import json


def create_visual_service(access_key_id: str, secret_access_key: str) -> VisualService:
    """
    创建 VisualService 实例
    
    Args:
        access_key_id: Access Key ID
        secret_access_key: Secret Access Key
    
    Returns:
        VisualService 实例
    """
    service = VisualService()
    service.set_ak(access_key_id)
    service.set_sk(secret_access_key)
    return service


def submit_video_task(
    service: VisualService,
    req_key: str,
    prompt: str,
    frames: int = 121,
    seed: int = -1,
    image_urls: Optional[list] = None,
    binary_data_base64: Optional[list] = None
) -> Dict[str, Any]:
    """
    提交视频生成任务（使用官方 SDK）
    
    根据官方示例：https://github.com/volcengine/volc-sdk-python/tree/main/volcengine/example/visual
    使用 cv_process 方法，SDK 会自动处理签名和请求
    
    Args:
        service: VisualService 实例
        req_key: 请求键（如 "jimeng_i2v_first_v30"）
        prompt: 提示词
        frames: 帧数（121 或 241）
        seed: 随机种子（-1 表示随机）
        image_urls: 图片 URL 列表
        binary_data_base64: Base64 编码的图片数据列表
    
    Returns:
        API 响应结果
    """
    # 构建请求参数
    params = {
        "req_key": req_key,
        "prompt": prompt,
        "frames": frames,
        "seed": seed,
    }
    
    # 添加图片输入（二选一）
    if binary_data_base64:
        params["binary_data_base64"] = binary_data_base64
    elif image_urls:
        params["image_urls"] = image_urls
    
    # 使用官方 SDK 的 cv_sync2async_submit_task 方法
    # SDK 会自动处理签名、Action、Version 等参数
    try:
        response = service.cv_sync2async_submit_task(params)
        return response
    except Exception as e:
        raise Exception(f"调用即梦 API 失败: {str(e)}")


def query_video_task(
    service: VisualService,
    req_key: str,
    task_id: str
) -> Dict[str, Any]:
    """
    查询视频生成任务状态（使用官方 SDK）
    
    Args:
        service: VisualService 实例
        req_key: 请求键（如 "jimeng_i2v_first_v30"）
        task_id: 任务 ID
    
    Returns:
        API 响应结果
    """
    params = {
        "req_key": req_key,
        "task_id": task_id,
    }
    
    try:
        # 使用官方 SDK 的 cv_sync2async_get_result 方法查询任务
        response = service.cv_sync2async_get_result(params)
        return response
    except Exception as e:
        raise Exception(f"查询任务失败: {str(e)}")

