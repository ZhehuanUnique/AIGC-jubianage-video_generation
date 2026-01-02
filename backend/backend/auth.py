"""
用户认证服务
"""
import os
import secrets
from sqlalchemy.orm import Session
from typing import Optional
from .database import User


class AuthService:
    """用户认证服务"""
    
    @staticmethod
    def get_user_by_api_key(db: Session, api_key: str) -> Optional[User]:
        """根据 API Key 获取用户"""
        return db.query(User).filter(
            User.api_key == api_key,
            User.is_active == True
        ).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据用户ID获取用户"""
        return db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
    
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> User:
        """创建新用户"""
        if not api_key:
            # 生成随机 API Key
            api_key = f"jubian_{secrets.token_urlsafe(32)}"
        
        user = User(
            username=username,
            email=email,
            api_key=api_key
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_or_create_default_user(db: Session) -> User:
        """获取或创建默认用户（单用户模式）"""
        # 查找默认用户
        default_user = db.query(User).filter(
            User.username == "default_user"
        ).first()
        
        if not default_user:
            # 创建默认用户
            default_user = AuthService.create_user(
                db,
                username="default_user",
                api_key=os.getenv("DEFAULT_API_KEY", "default_key")
            )
        
        return default_user

