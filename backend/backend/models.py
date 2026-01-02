"""
数据库模型定义
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime


class Asset(Base):
    """资产表"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    character_name = Column(String(100), nullable=False, index=True)
    view_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)  # 存储 URL 或路径
    file_url = Column(String(500), nullable=True)   # 如果使用云存储，存储完整 URL
    upload_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(20), nullable=True)   # 文件类型：image, video 等
    extra_metadata = Column(Text, nullable=True)    # JSON 格式的额外元数据（重命名，因为 metadata 是 SQLAlchemy 保留字）
    
    def to_dict(self):
        """转换为字典格式（兼容旧的 AssetMetadata 模型）"""
        return {
            "filename": self.filename,
            "character_name": self.character_name,
            "view_type": self.view_type,
            "file_path": self.file_path,
            "file_url": self.file_url or self.file_path,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "file_size": self.file_size,
            "id": self.id
        }

