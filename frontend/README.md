# 剧变时代 - 前端应用

基于 Vue 3 + Nuxt 3 + TypeScript + Tailwind CSS + Pinia 的视频生成前端应用。

## 技术栈

- **Vue 3**: 渐进式 JavaScript 框架
- **Nuxt 3**: Vue 3 的全栈框架
- **TypeScript**: 类型安全的 JavaScript
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Pinia**: Vue 的状态管理库

## 快速开始

### 方式一：使用启动脚本（推荐）

```bash
cd frontend-nuxt
./start.sh
```

### 方式二：手动启动

```bash
# 1. 安装依赖
npm install

# 2. 配置环境变量（可选）
# 创建 .env 文件，设置 BACKEND_URL
echo "BACKEND_URL=https://jubianai-backend.onrender.com" > .env

# 3. 启动开发服务器
npm run dev
```

访问 `http://localhost:3001` 查看应用。

## 开发命令

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 环境变量

创建 `.env` 文件：

```env
BACKEND_URL=https://jubianai-backend.onrender.com
```

## 部署

### Vercel 部署

#### 步骤 1: 在 Vercel 中部署 Nuxt 3 前端

1. **进入 Vercel Dashboard**
   - 访问 https://vercel.com/dashboard
   - 选择项目 `AIGC-jubianage` 或创建新项目

2. **配置项目设置**
   - **Root Directory**: 设置为 `frontend-nuxt`（**重要：没有尾部斜杠**）
   - **Framework Preset**: 选择 `Nuxt.js`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.output/public`
   - **Install Command**: `npm install`

3. **环境变量配置**
   在 Vercel 项目设置中添加环境变量：
   ```
   BACKEND_URL=https://jubianai-backend.onrender.com
   ```

#### 步骤 2: 配置自定义域名 jubianai.cn

1. **在 Vercel 中添加域名**
   - 进入项目设置 → Domains
   - 添加域名：`jubianai.cn` 和 `www.jubianai.cn`

2. **配置 DNS 记录**
   在域名注册商（如阿里云、腾讯云等）的 DNS 管理中添加：
   
   **CNAME 记录**：
   ```
   类型: CNAME
   主机记录: @ (或留空)
   记录值: cname.vercel-dns.com
   ```
   
   **www 子域名**：
   ```
   类型: CNAME
   主机记录: www
   记录值: cname.vercel-dns.com
   ```

3. **等待 DNS 生效**
   - DNS 记录通常需要几分钟到几小时生效
   - 可以在 Vercel Dashboard 中查看域名验证状态

#### 步骤 3: 验证部署

1. **检查部署状态**
   - 在 Vercel Dashboard 的 Deployments 页面查看最新部署
   - 确保状态为 "Ready"（绿色）

2. **访问测试**
   - 访问 `https://jubianai.cn` 应该显示新的 Nuxt 3 前端
   - 检查页面功能是否正常

### Netlify

1. 连接 GitHub 仓库
2. 构建命令：`npm run build`
3. 发布目录：`.output/public`

## 视频生成速度说明

### ⏱️ 视频生成时间

视频生成速度主要取决于 **即梦 AI API** 的处理能力，这是 API 服务端的限制，无法通过前端优化来加速。

#### 典型生成时间

- **5秒视频**：通常需要 **1-3 分钟**
- **10秒视频**：通常需要 **2-5 分钟**
- **15秒视频**：通常需要 **3-7 分钟**

#### 影响因素

1. **视频时长**：时长越长，生成时间越长
2. **分辨率**：1080P 比 720P 稍慢
3. **首尾帧**：有首尾帧的视频可能需要更多处理时间
4. **API 负载**：即梦 AI 服务器的当前负载情况
5. **网络延迟**：与 API 服务器的网络连接质量

### 🔄 当前优化措施

#### 1. 前端轮询机制

- **轮询间隔**：每 5 秒检查一次状态
- **最大轮询次数**：60 次（约 5 分钟）
- **自动刷新历史记录**：每 30 秒刷新一次，确保状态更新

#### 2. 状态提示优化

- 显示"生成中"状态
- 显示已等待时间
- 显示进度条和百分比
- 提供预计完成时间提示

#### 3. 重试机制

- API 调用失败时自动重试（最多 3 次）
- 每次重试间隔递增（2秒、4秒、6秒）

### ⚠️ 无法优化的部分

以下部分受 API 限制，无法通过前端优化：

1. **API 处理速度**：即梦 AI 的视频生成速度由服务端决定
2. **队列等待时间**：如果 API 服务器繁忙，可能需要排队
3. **网络传输**：视频文件从 API 服务器传输到后端需要时间

### 🔍 如何判断生成是否成功

#### 成功标志

- 状态从 "生成中" 变为 "已完成"
- 视频卡片显示视频预览
- 可以播放视频

#### 失败标志

- 状态显示 "生成失败"
- 错误信息提示
- 超过 10 分钟仍未完成（可能超时）

## 分辨率切换功能

### 功能说明

前端支持在 720P 和 1080P 之间切换：

- **720P**：默认分辨率，生成速度较快
- **1080P**：高清分辨率，生成速度稍慢

### 调试指南

如果无法切换 720P/1080P，请按以下步骤排查：

#### 1. 检查代码是否已部署

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看 Network 标签
3. 刷新页面
4. 查看加载的 JavaScript 文件
5. 搜索 `resolution` 或 `720p`，确认代码是否包含最新更改

**如果代码未更新**：
- 检查 Vercel 部署状态
- 确认代码已推送到 GitHub
- 等待 Vercel 重新部署完成

#### 2. 清除浏览器缓存

**方法 1：硬刷新**
- Windows/Linux: `Ctrl + Shift + R` 或 `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**方法 2：清除缓存**
1. 打开开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

#### 3. 检查按钮是否显示

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 使用元素选择器（Ctrl+Shift+C）
3. 查看控制栏区域
4. 确认是否有 720P 和 1080P 按钮

#### 4. 检查控制台错误

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签
3. 查看是否有红色错误信息

**常见错误**：
- `resolutions is not defined` - 变量未定义
- `resolution is not defined` - 变量未定义
- Vue 渲染错误

#### 5. 检查网络请求

**检查方法**：
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 点击分辨率按钮
4. 生成视频
5. 查看请求的 payload，确认是否包含 `resolution` 参数

**预期结果**：
```json
{
  "prompt": "...",
  "duration": 5,
  "resolution": "720p" 或 "1080p",
  ...
}
```

## 故障排除

### "Failed to fetch" 错误

#### 原因

1. **Render 免费实例休眠**
   - Render 免费计划的服务在空闲时会自动休眠
   - 首次请求需要 50 秒左右唤醒服务
   - 这是正常现象，不是错误

2. **网络连接问题**
   - 检查网络连接
   - 确认后端 URL 是否正确：`https://jubianai-backend.onrender.com`

3. **CORS 错误**
   - 后端已配置允许所有来源（`allow_origins=["*"]`）
   - 如果仍有问题，检查浏览器控制台

#### 解决方案

##### 1. 等待服务唤醒

如果看到 "Failed to fetch" 错误：
- 等待 50-60 秒
- 再次点击"生成视频"按钮
- 前端已实现自动重试机制（最多 3 次）

##### 2. 检查后端状态

访问后端健康检查端点：
```
https://jubianai-backend.onrender.com/health
```

应该返回：
```json
{"status": "healthy"}
```

##### 3. 查看后端日志

在 Render Dashboard 中查看服务日志，确认：
- 服务是否正在运行
- 是否有错误信息
- 请求是否到达后端

##### 4. 测试 API 端点

使用 curl 测试：
```bash
curl -X POST https://jubianai-backend.onrender.com/api/v1/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "测试视频",
    "duration": 5
  }'
```

### 其他常见问题

#### 1. 视频生成超时

- 5秒视频通常需要 1-3 分钟
- 10秒视频需要 2-5 分钟
- 前端会持续轮询状态，直到完成或超时

#### 2. 首尾帧上传失败

- 确保图片格式为 JPG、PNG
- 图片大小建议不超过 5MB
- 检查浏览器控制台的错误信息

#### 3. 状态轮询失败

- 检查网络连接
- 确认任务 ID 是否正确
- 查看后端日志中的任务状态

### 调试技巧

#### 浏览器控制台

打开浏览器开发者工具（F12），查看：
- Network 标签：查看 API 请求和响应
- Console 标签：查看 JavaScript 错误

#### 后端日志

在 Render Dashboard 中：
1. 进入服务页面
2. 点击 "Logs" 标签
3. 查看实时日志

## 本地测试

### 前置要求

1. **安装 Node.js**
   - 访问 [Node.js 官网](https://nodejs.org/) 下载并安装 LTS 版本（推荐 v18 或 v20）
   - 验证安装：
     ```bash
     node --version
     npm --version
     ```

### 安装依赖

```bash
cd frontend-nuxt
npm install
```

### 配置环境变量

创建 `.env` 文件（如果还没有）：

```env
BACKEND_URL=https://jubianai-backend.onrender.com
```

或者使用本地后端（如果本地运行）：

```env
BACKEND_URL=http://localhost:8000
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:3001` 启动。

### 测试功能

1. **打开浏览器**
   - 访问 `http://localhost:3001`
   - 应该看到"开启你的视频生成 剧变时代!"标题

2. **测试视频生成**
   - 在输入框中输入视频描述（例如："一个3D形象的小男孩，在公园滑滑板"）
   - 选择视频时长（5秒或10秒）
   - （可选）上传首帧和尾帧图片
   - 点击"生成视频"按钮

3. **检查功能**
   - ✅ 输入框正常显示
   - ✅ 首尾帧上传和预览
   - ✅ 生成按钮点击响应
   - ✅ 状态轮询（生成中、完成）
   - ✅ 视频播放和下载

### 常见问题

#### 1. 端口被占用

如果 3000 端口被占用，Nuxt 会自动使用下一个可用端口（如 3001）。

#### 2. 后端连接失败

- 检查 `.env` 文件中的 `BACKEND_URL` 是否正确
- 确认后端服务正在运行（Render 后端可能需要几秒钟启动）
- 检查浏览器控制台的网络请求

#### 3. CORS 错误

如果遇到 CORS 错误，需要确保后端 API 允许来自 `http://localhost:3001` 的请求。

#### 4. 依赖安装失败

```bash
# 清除缓存并重新安装
rm -rf node_modules package-lock.json
npm install
```

## 构建和部署问题

### Vercel 构建错误

#### 错误：路径中有双斜杠

```
Nuxt build error: Error: [vite:load-fallback] Could not load 
/vercel/path0/frontend-nuxt//assets/css/main.css
```

**解决方案**：

1. **检查 Vercel Root Directory 设置（最重要）**
   - 在 Vercel Dashboard → Settings → General
   - 确认 Root Directory 为 `frontend-nuxt`（**没有尾部斜杠**）
   - 如果显示为 `frontend-nuxt/`，改为 `frontend-nuxt`

2. **重新部署**
   - 在 Vercel Dashboard 中点击 "Redeploy"
   - 或推送新的提交触发自动部署

### Vercel 250MB 限制问题

#### 问题分析

Vercel 免费版限制：
- Serverless Function 未压缩大小不能超过 250MB
- 当前项目包含大量文件（后端代码、RAG 系统、视频文件等）

#### 解决方案

**在 Vercel 中修改项目设置**：
- **Root Directory**: 设置为 `frontend-nuxt`
- **Framework Preset**: 选择 `Nuxt.js`
- **Build Command**: `npm run build`（自动检测）
- **Output Directory**: `.output/public`（自动检测）

**确保 `.vercelignore` 正确**：
- 已创建 `frontend-nuxt/.vercelignore`
- 排除所有不必要的文件

### npm 弃用警告

这些警告来自构建过程中的依赖包，**不会阻止构建**，但建议处理以保持项目健康。

#### 警告列表

1. **keygrip@1.1.0** - 包已不再支持
2. **inflight@1.0.6** - 有内存泄漏问题，已弃用
3. **glob@7.2.3** - 需要升级到 v9+
4. **@koa/router@12.0.2** - 需要升级到 v15+

#### 解决方案

**方案 1: 更新所有依赖（推荐）**

```bash
cd frontend-nuxt

# 更新所有依赖到最新版本
npm update

# 或者使用 npm-check-updates 更新到最新兼容版本
npx npm-check-updates -u
npm install
```

**方案 2: 使用 npm audit fix**

```bash
cd frontend-nuxt

# 自动修复安全问题和依赖
npm audit fix

# 如果还有问题，尝试强制修复
npm audit fix --force
```

**方案 3: 忽略警告（临时方案）**

如果构建成功，这些警告可以暂时忽略。它们不会影响：
- ✅ 构建过程
- ✅ 部署到 Vercel
- ✅ 网站功能

**注意**: 长期来看，建议更新依赖以避免潜在的安全问题。

## Favicon 配置

### 文件结构

```
frontend-nuxt/
├── public/
│   ├── favicon.png          ✅
│   ├── favicon.svg          ✅
│   └── apple-touch-icon.png ✅
└── nuxt.config.ts           ✅ (已配置)
```

### 说明

- **favicon.png**: 传统浏览器使用
- **favicon.svg**: 现代浏览器优先使用（矢量图，更清晰）
- **apple-touch-icon.png**: iOS 设备添加到主屏幕时使用

### 验证方法

1. 访问网站
2. 查看浏览器标签页，应该能看到 favicon
3. 在 Vercel Dashboard 中，favicon 警告应该消失

## 快速部署命令

如果使用 Vercel CLI：

```bash
cd frontend-nuxt
npm install -g vercel
vercel --prod
```

然后在 Vercel Dashboard 中添加自定义域名。

## 注意事项

1. **SSL 证书**
   - Vercel 会自动为自定义域名配置 SSL 证书
   - 确保 DNS 记录正确后，SSL 证书会自动生成

2. **环境变量**
   - 确保在 Vercel 中设置了 `BACKEND_URL`
   - 生产环境使用：`https://jubianai-backend.onrender.com`

3. **构建优化**
   - Nuxt 3 会自动优化构建
   - 确保 `package.json` 中的依赖正确
