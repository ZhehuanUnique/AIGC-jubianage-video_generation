"""
对象存储服务
支持腾讯云 COS、阿里云 OSS 和亚马逊 S3
"""
import os
from typing import Optional
from pathlib import Path
import logging
import httpx

logger = logging.getLogger(__name__)


class StorageService:
    """对象存储服务基类"""
    
    async def upload_video(self, video_url: str, video_name: str) -> Optional[str]:
        """
        上传视频到对象存储
        
        Args:
            video_url: 视频URL（从即梦API获取）
            video_name: 视频名称（用于对象存储中的文件名）
            
        Returns:
            对象存储中的URL，如果上传失败返回None
        """
        raise NotImplementedError
    
    async def download_file(self, url: str) -> bytes:
        """下载文件（用于上传到对象存储）"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=300)
            response.raise_for_status()
            return response.content


class TencentCOSStorage(StorageService):
    """腾讯云 COS 存储服务"""
    
    def __init__(self):
        from qcloud_cos import CosConfig
        from qcloud_cos import CosS3Client
        from qcloud_cos.cos_exception import CosClientError, CosServiceError
        
        self.secret_id = os.getenv("COS_SECRET_ID")
        self.secret_key = os.getenv("COS_SECRET_KEY")
        self.region = os.getenv("COS_REGION")  # 如: ap-guangzhou
        self.bucket_name = os.getenv("COS_BUCKET")
        self.bucket_domain = os.getenv("COS_BUCKET_DOMAIN")  # CDN域名（可选）
        
        if not all([self.secret_id, self.secret_key, self.region, self.bucket_name]):
            raise ValueError("请配置腾讯云 COS 环境变量：COS_SECRET_ID, COS_SECRET_KEY, COS_REGION, COS_BUCKET")
        
        # 初始化 COS 配置
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme='https'  # 使用 HTTPS
        )
        
        # 初始化 COS 客户端
        self.cos_client = CosS3Client(config)
    
    async def upload_video(self, video_url: str, video_name: str) -> Optional[str]:
        """上传视频到腾讯云 COS"""
        try:
            # 下载视频
            import requests
            response = requests.get(video_url, timeout=300)  # 5分钟超时
            response.raise_for_status()
            video_data = response.content
            
            # 上传到 COS（同步操作）
            object_key = f"videos/{video_name}"
            
            # 上传文件
            self.cos_client.put_object(
                Bucket=self.bucket_name,
                Body=video_data,
                Key=object_key,
                ContentType='video/mp4'
            )
            
            # 返回 COS URL
            if self.bucket_domain:
                # 使用 CDN 域名
                return f"https://{self.bucket_domain}/{object_key}"
            else:
                # 使用 COS 域名
                # 格式: https://{bucket}.cos.{region}.myqcloud.com/{object_key}
                return f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{object_key}"
                
        except Exception as e:
            logger.error(f"上传视频到腾讯云 COS 失败: {str(e)}")
            return None


class AliyunOSSStorage(StorageService):
    """阿里云 OSS 存储服务"""
    
    def __init__(self):
        import oss2
        
        self.access_key_id = os.getenv("ALIYUN_OSS_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("ALIYUN_OSS_ACCESS_KEY_SECRET")
        self.bucket_name = os.getenv("ALIYUN_OSS_BUCKET_NAME")
        self.endpoint = os.getenv("ALIYUN_OSS_ENDPOINT")  # 如: oss-cn-beijing.aliyuncs.com
        self.bucket_domain = os.getenv("ALIYUN_OSS_BUCKET_DOMAIN")  # CDN域名（可选）
        
        if not all([self.access_key_id, self.access_key_secret, self.bucket_name, self.endpoint]):
            raise ValueError("请配置阿里云 OSS 环境变量：ALIYUN_OSS_ACCESS_KEY_ID, ALIYUN_OSS_ACCESS_KEY_SECRET, ALIYUN_OSS_BUCKET_NAME, ALIYUN_OSS_ENDPOINT")
        
        # 初始化 OSS 客户端
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(auth, f"https://{self.endpoint}", self.bucket_name)
    
    async def upload_video(self, video_url: str, video_name: str) -> Optional[str]:
        """上传视频到阿里云 OSS"""
        try:
            # 下载视频（使用同步 requests，因为 OSS 客户端是同步的）
            import requests
            response = requests.get(video_url, timeout=300)  # 5分钟超时
            response.raise_for_status()
            video_data = response.content
            
            # 上传到 OSS（同步操作）
            object_key = f"videos/{video_name}"
            result = self.bucket.put_object(object_key, video_data)
            
            if result.status == 200:
                # 返回 OSS URL
                if self.bucket_domain:
                    # 使用 CDN 域名
                    return f"https://{self.bucket_domain}/{object_key}"
                else:
                    # 使用 OSS 域名
                    return f"https://{self.bucket_name}.{self.endpoint}/{object_key}"
            else:
                logger.error(f"OSS 上传失败: status={result.status}")
                return None
                
        except Exception as e:
            logger.error(f"上传视频到 OSS 失败: {str(e)}")
            return None


class S3Storage(StorageService):
    """亚马逊 S3 存储服务"""
    
    def __init__(self):
        import boto3
        from botocore.exceptions import ClientError
        
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.region = os.getenv("AWS_S3_REGION", "us-east-1")
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            raise ValueError("请配置 AWS S3 环境变量：AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME")
        
        # 初始化 S3 客户端
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region
        )
    
    async def upload_video(self, video_url: str, video_name: str) -> Optional[str]:
        """上传视频到亚马逊 S3"""
        try:
            # 下载视频（使用同步 requests，因为 boto3 是同步的）
            import requests
            response = requests.get(video_url, timeout=300)  # 5分钟超时
            response.raise_for_status()
            video_data = response.content
            
            # 上传到 S3（同步操作）
            object_key = f"videos/{video_name}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=video_data,
                ContentType='video/mp4'
            )
            
            # 返回 S3 URL
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_key}"
            
        except Exception as e:
            logger.error(f"上传视频到 S3 失败: {str(e)}")
            return None


def get_storage_service() -> Optional[StorageService]:
    """
    根据环境变量获取存储服务实例
    
    优先使用腾讯云 COS，如果未配置则尝试其他存储服务
    """
    storage_type = os.getenv("STORAGE_TYPE", "tencent_cos").lower()
    
    # 优先使用腾讯云 COS
    if storage_type == "tencent_cos" or storage_type == "cos":
        try:
            return TencentCOSStorage()
        except ValueError as e:
            logger.warning(f"腾讯云 COS 未配置: {e}")
            # 如果未配置 COS，尝试其他存储服务
            storage_type = "aliyun_oss"
    
    # 使用阿里云 OSS
    if storage_type == "aliyun_oss":
        try:
            return AliyunOSSStorage()
        except ValueError:
            logger.warning("阿里云 OSS 未配置，尝试使用 S3")
            storage_type = "s3"
    
    # 使用亚马逊 S3
    if storage_type == "s3":
        try:
            return S3Storage()
        except ValueError:
            logger.warning("AWS S3 未配置，对象存储功能不可用")
            return None
    
    return None

