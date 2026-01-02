#!/bin/bash
# Render 启动脚本
# 确保 uvicorn 已安装并启动服务

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 启动 uvicorn
exec uvicorn jubianai.backend.api:app --host 0.0.0.0 --port ${PORT:-10000}


