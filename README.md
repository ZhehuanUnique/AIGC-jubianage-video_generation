# 即梦 AI 视频生成平台

基于即梦 AI（火山引擎）的视频生成服务，支持首尾帧控制、720P/1080P 分辨率、视频增强等功能。

## 📁 项目结构

```
AIGC-jubianage-video_generation/
├── backend/          # Python FastAPI 后端
│   ├── backend/      # 核心业务逻辑
│   ├── config.py     # 配置文件
│   ├── requirements.txt
│   └── ...
├── frontend/         # Nuxt.js 前端
│   ├── pages/        # 页面
│   ├── stores/       # 状态管理
│   └── ...
└── README.md
```

## 🚀 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# 编辑 .env 文件，填入即梦 API 密钥
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3001

## 🔑 配置说明

### 即梦 API 配置

在 `backend/.env` 文件中配置：

```env
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key
JIMENG_API_ENDPOINT=https://visual.volcengineapi.com
```

### 数据库配置（可选）

```env
SUPABASE_DB_URL=postgresql://postgres:password@host:5432/postgres
```

## 📚 功能特性

- 🎬 视频生成：基于即梦 AI 3.0/3.0 Pro
- 🖼️ 首尾帧控制：支持上传首帧和尾帧图片
- 📊 历史记录：自动保存视频生成历史
- ⭐ 收藏和点赞：支持收藏和点赞视频
- 🚀 视频增强：超分辨率和帧率提升
- 📱 响应式设计：支持桌面和移动设备

## 🌐 部署

### Vercel 部署（前端）

1. 连接 GitHub 仓库到 Vercel
2. 设置 Root Directory: `frontend`
3. 设置环境变量 `BACKEND_URL`

### Render 部署（后端）

1. 连接 GitHub 仓库
2. 设置 Root Directory: `backend`
3. 配置环境变量
4. 设置启动命令：`python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT`

## 📖 更多文档

- [后端文档](./backend/README.md)
- [前端文档](./frontend/README.md)

## 📄 许可证

MIT

