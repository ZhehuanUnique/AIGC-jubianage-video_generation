# 更新后端 URL 配置

## 问题
前端仍然尝试连接 `http://localhost:8000`，但后端已改为 `8001` 端口。

## 解决方案

### 方案 1：本地开发环境

如果是在本地运行前端，需要：

1. **创建或更新 `.env` 文件**（在 `frontend` 目录下）：
   ```env
   BACKEND_URL=http://localhost:8001
   ```

2. **重启前端开发服务器**：
   ```bash
   cd frontend
   npm run dev
   ```

3. **清除浏览器缓存**：
   - 按 `Ctrl + Shift + R` 强制刷新
   - 或打开开发者工具 → Application → Clear storage

### 方案 2：Vercel 部署环境

如果访问的是 Vercel 部署的前端，需要在 Vercel 中设置环境变量：

1. 访问 Vercel Dashboard
2. 进入项目设置 → Environment Variables
3. 添加环境变量：
   - Key: `BACKEND_URL`
   - Value: `http://localhost:8001`（本地）或你的后端服务器地址
   - Environment: Production, Preview, Development（全选）

4. 重新部署项目以应用新配置

### 方案 3：检查当前配置

前端通过 `useRuntimeConfig()` 获取后端 URL，配置在 `nuxt.config.ts` 中：

```typescript
runtimeConfig: {
  public: {
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8001'
  }
}
```

优先级：
1. 环境变量 `BACKEND_URL`（最高优先级）
2. 默认值 `http://localhost:8001`

### 快速修复（本地开发）

在 `frontend` 目录下运行：

```bash
# Windows PowerShell
echo "BACKEND_URL=http://localhost:8001" > .env

# 然后重启前端
npm run dev
```

