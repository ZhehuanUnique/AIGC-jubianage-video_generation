# 即梦 AI 视频生成平台

基于即梦 AI（火山引擎）的视频生成服务，支持首尾帧控制、720P/1080P 分辨率、视频增强等功能。

## 🌐 在线访问

**生产环境：** [https://aigc-jubianage-video-generation.vercel.app/](https://aigc-jubianage-video-generation.vercel.app/)

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

### 环境要求

- **Python**: 3.8+
- **Node.js**: 18+ (推荐 LTS 版本)
- **即梦 API 密钥**: 需要火山引擎账号并开通即梦服务

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# 编辑 .env 文件，填入即梦 API 密钥
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:3001` 启动。

**提示：** 前端需要配置 `BACKEND_URL` 环境变量指向后端服务地址。

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

- 🎬 **视频生成**：基于即梦 AI 3.0pro/3.5pro，支持 5秒/10秒 视频生成
- 🖼️ **首尾帧控制**：支持上传首帧和尾帧图片，精确控制视频开头和结尾
- 📊 **历史记录**：自动保存视频生成历史，支持查看、播放、下载
- ⭐ **收藏和点赞**：支持收藏和点赞喜欢的视频
- 🚀 **视频增强**：
  - 超分辨率：支持 Real-ESRGAN 和 Waifu2x，可将 1080P 提升至 4K
  - 帧率提升：支持 RIFE 和 FILM 插帧，可将 24fps 提升至 60fps
- 📱 **响应式设计**：完美支持桌面和移动设备
- 🎨 **多分辨率支持**：720P 和 1080P 可选

## 🛠️ 技术栈

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Nuxt 3**: Vue 3 的全栈框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Pinia**: Vue 状态管理

### 后端
- **FastAPI**: 现代 Python Web 框架
- **PostgreSQL**: 数据库（通过 Supabase）
- **即梦 AI API**: 视频生成服务
- **火山引擎 SDK**: API 认证和调用

## 🌐 部署

### Vercel 部署（前端）

前端已部署在 Vercel，访问地址：[https://aigc-jubianage-video-generation.vercel.app/](https://aigc-jubianage-video-generation.vercel.app/)

**部署步骤：**

1. 连接 GitHub 仓库到 Vercel
2. 设置 **Root Directory**: `frontend`（重要：不要带尾部斜杠）
3. 设置环境变量：
   - `BACKEND_URL`: 后端服务地址（如 `https://your-backend.onrender.com`）
4. Framework Preset 选择 `Nuxt.js`
5. Build Command: `npm run generate`
6. Output Directory: `.output/public`

**详细部署文档：** 参见 [frontend/README.md](./frontend/README.md)

### Render 部署（后端）

**部署步骤：**

1. 连接 GitHub 仓库到 Render
2. 设置 **Root Directory**: `backend`
3. 配置环境变量（参见 [backend/README.md](./backend/README.md)）：
   - `VOLCENGINE_ACCESS_KEY_ID`: 火山引擎 Access Key ID
   - `VOLCENGINE_SECRET_ACCESS_KEY`: 火山引擎 Secret Access Key
   - `SUPABASE_DB_URL`: Supabase 数据库连接字符串（可选）
   - `DEFAULT_API_KEY`: 默认 API Key（可选）
4. 设置启动命令：`python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
5. 健康检查路径：`/health`

**详细部署文档：** 参见 [backend/README.md](./backend/README.md)

## 📖 更多文档

- [后端文档](./backend/README.md) - 详细的 API 配置、数据库设置、部署指南
- [前端文档](./frontend/README.md) - 前端开发、部署、故障排除指南

## 🔗 相关链接

- [即梦 API 文档](https://www.volcengine.com/docs/85621?lang=zh)
- [火山引擎控制台](https://console.volcengine.com/)
- [Supabase 文档](https://supabase.com/docs)
- [Vercel 文档](https://vercel.com/docs)
- [Render 文档](https://render.com/docs)

## 📄 许可证

MIT

---

**最后更新：** 2025-01-XX

