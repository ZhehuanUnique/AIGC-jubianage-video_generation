"""
火山引擎 API 签名认证工具
用于即梦 AI API 的 AK/SK 认证
参考：https://www.volcengine.com/docs/6444/1340578?lang=zh
"""
import hmac
import hashlib
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import quote


def sign(key: bytes, msg: str) -> bytes:
    """HMAC-SHA256 签名"""
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
    """生成签名密钥"""
    k_date = sign(key.encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'request')
    return k_signing


def format_query(parameters: Dict[str, Any]) -> str:
    """
    格式化查询参数（按照官方 Python 签名示例）
    参考：https://github.com/volcengine/volc-openapi-demos/blob/main/signature/python/sign.py
    """
    if not parameters:
        return ""
    # 按照官方示例 norm_query 函数的方式
    # 使用 quote 进行 URL 编码，并替换 + 为 %20
    query = ""
    for key in sorted(parameters.keys()):
        if isinstance(parameters[key], list):
            for k in parameters[key]:
                query = query + quote(str(key), safe="-_.~") + "=" + quote(str(k), safe="-_.~") + "&"
        else:
            query = query + quote(str(key), safe="-_.~") + "=" + quote(str(parameters[key]), safe="-_.~") + "&"
    query = query[:-1]  # 移除最后的 &
    return query.replace("+", "%20")


def generate_signature(
    access_key_id: str,
    secret_access_key: str,
    method: str,
    uri: str,
    query: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    body: str = "",
    host: str = "cv.volcengineapi.com",
    region: str = "cn-north-1",
    service: str = "cv"
) -> Dict[str, str]:
    """
    生成火山引擎 API 签名（V4 签名算法）
    
    参考：https://www.volcengine.com/docs/6444/1340578?lang=zh
    
    Args:
        access_key_id: Access Key ID
        secret_access_key: Secret Access Key
        method: HTTP 方法 (GET, POST, etc.)
        uri: 请求 URI 路径（通常为 '/'）
        query: 查询参数
        headers: 请求头
        body: 请求体字符串
        host: API 主机名
        region: 区域
        service: 服务名称
    
    Returns:
        包含签名信息的字典，用于设置请求头
    """
    # Secret Access Key 处理
    # 根据官方 Python 签名示例：https://github.com/volcengine/volc-openapi-demos/blob/main/signature/python/sign.py
    # Secret Key 直接使用，不需要 base64 解码！
    # 官方示例：credential["secret_access_key"].encode("utf-8")
    secret_key = secret_access_key
    
    # 时间戳 - 使用 ISO 8601 格式
    t = datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')
    
    # 规范化 URI（通常为 '/'）
    canonical_uri = uri if uri else '/'
    
    # 规范化查询字符串
    formatted_query = format_query(query) if query else ""
    canonical_querystring = formatted_query
    
    # 计算请求体哈希
    payload_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
    
    # 规范化请求头
    content_type = headers.get('Content-Type', 'application/json') if headers else 'application/json'
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    canonical_headers = (
        f'content-type:{content_type}\n'
        f'host:{host}\n'
        f'x-content-sha256:{payload_hash}\n'
        f'x-date:{current_date}\n'
    )
    
    # 构建规范请求
    canonical_request = (
        f"{method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )
    
    # 计算签名
    algorithm = 'HMAC-SHA256'
    credential_scope = f"{datestamp}/{region}/{service}/request"
    string_to_sign = (
        f"{algorithm}\n"
        f"{current_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )
    
    # 生成签名密钥
    signing_key = get_signature_key(secret_key, datestamp, region, service)
    
    # 计算最终签名
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # 构建 Authorization 头
    authorization_header = (
        f"{algorithm} "
        f"Credential={access_key_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    
    return {
        'X-Date': current_date,
        'Authorization': authorization_header,
        'X-Content-Sha256': payload_hash,
        'Content-Type': content_type
    }


def generate_simple_signature(
    access_key_id: str,
    secret_access_key: str,
    method: str,
    uri: str,
    body: str = ""
) -> Dict[str, str]:
    """
    简化版签名（备用方案）
    
    如果标准签名失败，可以尝试这个简化版本
    """
    # 解码 Secret Access Key
    try:
        secret_key = base64.b64decode(secret_access_key).decode('utf-8')
    except Exception:
        secret_key = secret_access_key
    
    # 时间戳
    timestamp = str(int(time.time()))
    
    # 构建待签名字符串
    string_to_sign = f"{method}\n{uri}\n{body}\n{timestamp}"
    
    # 计算签名
    signature = base64.b64encode(
        hmac.new(
            secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return {
        "Authorization": f"HMAC-SHA256 Credential={access_key_id}, Signature={signature}",
        "X-Date": timestamp,
    }
