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
    # 注意：binary_data_base64 必须是字符串列表，每个元素是base64编码的图片数据
    params = {
        "req_key": req_key,
        "prompt": prompt,
        "frames": frames,
        "seed": seed,
    }
    
    # 添加图片输入（二选一）
    # 确保 binary_data_base64 是列表格式，且每个元素都是字符串
    if binary_data_base64:
        # 确保是列表且每个元素都是字符串
        if isinstance(binary_data_base64, list):
            # 过滤掉空值，确保所有元素都是非空字符串
            binary_data_base64 = [str(item) for item in binary_data_base64 if item]
            if binary_data_base64:
                params["binary_data_base64"] = binary_data_base64
        else:
            # 如果不是列表，转换为列表
            params["binary_data_base64"] = [str(binary_data_base64)]
    elif image_urls:
        # 确保 image_urls 是列表格式
        if isinstance(image_urls, list):
            image_urls = [str(url) for url in image_urls if url]
            if image_urls:
                params["image_urls"] = image_urls
        else:
            params["image_urls"] = [str(image_urls)]
    
    # 使用官方 SDK 的 cv_sync2async_submit_task 方法
    # SDK 会自动处理签名、Action、Version 等参数
    try:
        # 打印调试信息
        print(f"[DEBUG] 提交参数: req_key={req_key}, prompt长度={len(prompt)}, frames={frames}, seed={seed}")
        print(f"[DEBUG] 图片数据: binary_data_base64={bool(params.get('binary_data_base64'))}, image_urls={bool(params.get('image_urls'))}")
        if params.get("binary_data_base64"):
            print(f"[DEBUG] binary_data_base64 数量: {len(params['binary_data_base64'])}, 第一张长度: {len(params['binary_data_base64'][0]) if params['binary_data_base64'] else 0}")
        
        response = service.cv_sync2async_submit_task(params)
        return response
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] SDK 调用失败: {error_msg}")
        # 如果是解析错误，提供更详细的错误信息
        if "parsing" in error_msg.lower() or "parse" in error_msg.lower():
            raise Exception(f"调用即梦 API 失败: 请求参数解析错误 - {error_msg}。请检查 binary_data_base64 格式是否正确（应为base64字符串列表）")
        raise Exception(f"调用即梦 API 失败: {error_msg}")


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

