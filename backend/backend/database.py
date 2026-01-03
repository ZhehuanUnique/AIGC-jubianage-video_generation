"""
数据库配置和连接
使用 Supabase PostgreSQL
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# Supabase 数据库连接字符串格式：
# postgresql://postgres:[YOUR-PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_DB_URL = os.getenv(
    "SUPABASE_DB_URL",
    os.getenv("DATABASE_URL")  # 兼容 Render 等平台的 DATABASE_URL
)

# 数据库连接变为可选，如果没有配置则使用 None
# 这样后端可以在没有数据库的情况下启动
engine = None
if SUPABASE_DB_URL:
    try:
        # 创建数据库引擎
        # 注意：如果遇到 IPv6 连接问题，请使用 Supabase Connection Pooling（端口 6543）
        # Connection Pooling URL 格式：
        # postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
        engine = create_engine(
            SUPABASE_DB_URL,
            pool_pre_ping=True,  # 连接前检查连接是否有效
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,  # 1小时后回收连接
            connect_args={
                "connect_timeout": 10,
                "sslmode": "require"  # Supabase 需要 SSL
            }
        )
        
        # 测试连接
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("[SUCCESS] 数据库连接成功")
        except Exception as test_error:
            error_msg = str(test_error)
            print(f"[ERROR] 数据库连接测试失败: {error_msg}")
            
            # 检查是否是 IPv6 连接问题
            if "Network is unreachable" in error_msg or "IPv6" in error_msg or "2406:" in error_msg:
                print("[WARN] 检测到 IPv6 连接问题")
                print("[INFO] 解决方案：请使用 Supabase Connection Pooling URL（端口 6543）")
                print("   在 Supabase Dashboard → Settings → Database → Connection Pooling")
                print("   复制 Connection String（使用端口 6543 的那个）")
                print("   然后在 Render Dashboard 中更新 SUPABASE_DB_URL 环境变量")
            
            raise test_error
                
    except Exception as e:
        print(f"警告: 数据库连接失败: {str(e)}")
        print("后端将在没有数据库的情况下运行，历史记录功能将不可用")
        import traceback
        traceback.print_exc()
        engine = None
else:
    print("警告: SUPABASE_DB_URL 未设置，数据库功能将不可用")
    print("历史记录功能需要配置数据库，请参考 SUPABASE_SETUP.md")

# 创建会话工厂（如果引擎存在）
SessionLocal = None
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))  # 如果使用密码登录
    api_key = Column(String(255), unique=True, index=True)  # API密钥
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class VideoGeneration(Base):
    """视频生成历史表"""
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)  # 即梦 API 返回的任务ID
    user_id = Column(Integer, nullable=False, index=True)  # 用户ID
    
    # 生成参数
    prompt = Column(Text, nullable=False)  # 提示词
    negative_prompt = Column(Text, nullable=True)  # 负面提示词
    duration = Column(Integer, nullable=False)  # 视频时长（秒）
    fps = Column(Integer, default=24)  # 帧率
    width = Column(Integer, default=720)  # 宽度
    height = Column(Integer, default=720)  # 高度
    seed = Column(Integer, nullable=True)  # 随机种子
    
    # 首尾帧
    first_frame_url = Column(Text, nullable=True)  # 首帧图片URL（base64或URL）
    last_frame_url = Column(Text, nullable=True)  # 尾帧图片URL（base64或URL）
    
    # 视频信息
    video_url = Column(Text, nullable=True)  # 生成的视频URL（对象存储URL）
    video_name = Column(String(255), nullable=True)  # 视频名称
    video_size = Column(Integer, nullable=True)  # 视频大小（字节）
    
    # 状态
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending/processing/completed/failed
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 扩展元数据（使用 name 参数映射到数据库的 metadata 列）
    extra_metadata = Column('metadata', JSON, nullable=True)  # 扩展元数据（JSON格式）
    
    # 用户操作标记
    is_ultra_hd = Column(Boolean, default=False)  # 是否已超清
    is_favorite = Column(Boolean, default=False)  # 是否收藏
    is_liked = Column(Boolean, default=False)  # 是否点赞


# 数据库依赖注入
def get_db():
    """获取数据库会话"""
    if not SessionLocal:
        raise HTTPException(
            status_code=503,
            detail="数据库未配置。请设置 SUPABASE_DB_URL 环境变量。"
        )
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化数据库表
def init_db():
    """初始化数据库表（创建表）"""
    if not engine:
        raise ValueError("数据库未配置，无法初始化表。请设置 SUPABASE_DB_URL 环境变量。")
    Base.metadata.create_all(bind=engine)

