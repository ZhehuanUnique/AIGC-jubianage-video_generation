"""
数据库初始化脚本
运行此脚本来创建数据库表
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database import init_db, engine
from backend.models import Base

if __name__ == "__main__":
    # 设置 Windows 控制台编码为 UTF-8
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("正在初始化数据库...")
    try:
        init_db()
        print("[SUCCESS] 数据库表创建成功！")
    except Exception as e:
        print(f"[ERROR] 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

