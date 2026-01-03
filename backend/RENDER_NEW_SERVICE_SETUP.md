# Render 新后端服务创建指南

## 问题说明

当前 Render 后端服务连接的是 `AIGC-jubianage` 仓库，但实际项目是 `AIGC-jubianage-video_generation` 仓库，导致代码更新无法自动部署。

## 解决方案：创建新的 Render 后端服务

### 步骤 1: 在 Render Dashboard 创建新服务

1. **访问 Render Dashboard**
   - 打开 https://dashboard.render.com/
   - 登录你的账户

2. **创建新的 Web Service**
   - 点击右上角的 **"New +"** 按钮
   - 选择 **"Web Service"**

3. **连接 GitHub 仓库**
   - 选择 **"Connect GitHub"** 或 **"Connect a repository"**
   - 选择仓库：`ZhehuanUnique / AIGC-jubianage-video_generation`
   - 点击 **"Connect"**

### 步骤 2: 配置服务设置

#### 基本设置

- **Name（服务名称）**: `aigc-video-backend` 或 `jubianai-video-backend`
- **Region（地区）**: `Oregon`（或选择离你最近的地区）
- **Branch（分支）**: `main`
- **Root Directory（根目录）**: `backend` ⚠️ **重要：必须填写**
- **Runtime（运行时）**: `Python 3`
- **Build Command（构建命令）**: 
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- **Start Command（启动命令）**: 
  ```bash
  python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT
  ```
- **Plan（计划）**: `Free`（免费版）

#### 健康检查

- **Health Check Path**: `/health`

### 步骤 3: 配置环境变量

在服务创建页面或创建后的 **Environment** 标签页中添加以下环境变量：

#### 必需的环境变量

```bash
# 即梦 API（火山引擎）
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key

# 即梦 API 版本配置
JIMENG_VIDEO_VERSION=3.5pro

# Seedance API Keys
DOUBAO_SEEDANCE_1_0_LITE_API_KEY=sk-DzzAX3YmhTZG8BV7GTo3qgvkh6cye1fJty1igEChHxmv8NVu
DOUBAO_SEEDANCE_1_5_PRO_API_KEY=sk-4qOfXiYXE2EHRW1QDmfIhlTaWLwdIc5dTmR3QRcsuKztCE4R

# Supabase 数据库
SUPABASE_DB_URL=postgresql://postgres.ogndfzxtzsifaqwzfojs:2003419519CFF@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# 默认用户 API Key
DEFAULT_API_KEY=default_key

# 对象存储（腾讯云 COS）
STORAGE_TYPE=tencent_cos
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=ap-guangzhou
COS_BUCKET=jubianage-1392491103
COS_BUCKET_DOMAIN=your-cdn-domain.com

# 后端服务端口（Render 会自动设置 PORT 环境变量）
# PORT 由 Render 自动管理，不需要手动设置
```

#### 可选的环境变量

```bash
# CORS 配置（如果需要额外的允许源）
CORS_ORIGINS=https://example.com,https://another-domain.com

# MCP 服务配置（用于修复历史记录）
SUPABASE_PROJECT_REF=sggdokxjqycskeybyqvv
SUPABASE_ACCESS_TOKEN=sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03
VERCEL_TOKEN=bUFnjiVqrAvBYZyTmED7Q9wl
RENDER_API_KEY=rnd_QtPtywDxKnQAUCABtvIwBiwf0lvX
```

### 步骤 4: 创建服务并等待部署

1. 点击 **"Create Web Service"** 按钮
2. Render 会自动：
   - 从 GitHub 拉取代码
   - 安装依赖
   - 构建项目
   - 启动服务
3. 等待部署完成（通常需要 2-5 分钟）

### 步骤 5: 获取服务 URL

部署完成后，Render 会提供一个 URL，格式类似：
```
https://aigc-video-backend-xxxx.onrender.com
```

### 步骤 6: 更新 Vercel 环境变量

1. 访问 Vercel Dashboard
2. 进入项目 `aigc-jubianage-video-generation`
3. 进入 **Settings** → **Environment Variables**
4. 更新 `BACKEND_URL` 环境变量：
   ```
   BACKEND_URL=https://aigc-video-backend-xxxx.onrender.com
   ```
   （将 `xxxx` 替换为实际的服务 ID）
5. 重新部署 Vercel 项目以应用新配置

### 步骤 7: 验证部署

1. **测试健康检查**
   ```bash
   curl https://aigc-video-backend-xxxx.onrender.com/health
   ```
   应该返回：`{"status": "healthy"}`

2. **测试 CORS**
   - 打开浏览器开发者工具
   - 访问 Vercel 前端：`https://aigc-jubianage-video-generation.vercel.app/`
   - 检查控制台，应该不再有 CORS 错误
   - 历史记录应该能正常加载

## 注意事项

1. **Root Directory 必须正确**
   - 必须设置为 `backend`（不带斜杠）
   - 这样 Render 才能找到 `requirements.txt` 和 `backend/api.py`

2. **环境变量优先级**
   - Render 环境变量会覆盖代码中的默认值
   - 确保所有必需的环境变量都已设置

3. **免费版限制**
   - Render 免费版服务在空闲时会自动休眠
   - 首次请求可能需要 50 秒左右唤醒
   - 这是正常现象

4. **自动部署**
   - 服务创建后，每次推送到 `main` 分支都会自动触发部署
   - 确保 GitHub 仓库连接正确

## 故障排除

### 部署失败

1. **检查构建日志**
   - 在 Render Dashboard 中查看构建日志
   - 确认依赖安装是否成功
   - 检查是否有 Python 版本不兼容问题

2. **检查启动命令**
   - 确认 `startCommand` 正确
   - 确认模块路径正确：`backend.api:app`

3. **检查环境变量**
   - 确认所有必需的环境变量都已设置
   - 检查环境变量值是否正确（无多余空格）

### CORS 仍然失败

1. **确认后端 URL 已更新**
   - 检查 Vercel 环境变量 `BACKEND_URL` 是否指向新服务
   - 重新部署 Vercel 项目

2. **检查后端日志**
   - 在 Render Dashboard 中查看服务日志
   - 确认 CORS 中间件已正确加载

3. **清除浏览器缓存**
   - 按 `Ctrl + Shift + R` 强制刷新
   - 或使用无痕模式测试

## 完成后的操作

1. ✅ 新服务创建并部署成功
2. ✅ 更新 Vercel 的 `BACKEND_URL` 环境变量
3. ✅ 重新部署 Vercel 前端
4. ✅ 测试历史记录加载功能
5. ✅ （可选）删除旧的 Render 服务以节省资源

