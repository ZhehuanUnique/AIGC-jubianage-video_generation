#!/bin/bash

# 快速启动脚本

echo "🚀 启动剧变时代前端应用..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    echo "BACKEND_URL=http://localhost:8000" > .env
    echo "✅ .env 文件已创建，使用默认后端 URL (localhost)"
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
echo "访问: http://localhost:3001"
npm run dev

