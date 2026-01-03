# 剧变时代 (Jubianai) - 视频生成后端

基于即梦 AI 的视频生成服务，支持 720P/1080P 分辨率、视频增强（超分辨率和插帧）等功能。

## 📋 目录

- [快速开始](#快速开始)
- [API 配置](#api-配置)
- [数据库配置](#数据库配置)
- [功能说明](#功能说明)
- [部署指南](#部署指南)
- [故障排除](#故障排除)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd jubianai
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 即梦 API 配置
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key

# 数据库配置（可选）
SUPABASE_DB_URL=postgresql://postgres:password@host:5432/postgres

# 对象存储（可选）
STORAGE_TYPE=aliyun_oss
ALIYUN_OSS_ACCESS_KEY_ID=your_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret
ALIYUN_OSS_BUCKET_NAME=your_bucket
```

### 3. 启动服务

```bash
# 后端服务
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8001
```

---

## 🔑 API 配置

### 即梦 API 密钥配置

#### 获取 API 密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 进入 **访问控制** > **密钥管理**
3. 创建或查看 Access Key ID 和 Secret Access Key

#### 配置方法

**方法 1: 本地开发（.env 文件）**

在 `jubianai/.env` 文件中添加：

```bash
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id_here
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key_here
```

**方法 2: 部署环境（Render/Railway）**

在部署平台的环境变量设置中添加：
- `VOLCENGINE_ACCESS_KEY_ID`
- `VOLCENGINE_SECRET_ACCESS_KEY`

#### 验证配置

重启服务后，尝试生成视频。如果配置正确，应该不再出现 "Access Denied" 错误。

### Access Denied (50400) 错误修复

如果遇到 `50400 Access Denied` 错误，请检查：

1. ✅ 环境变量名称是否正确（区分大小写）
2. ✅ 密钥值是否正确（无多余空格）
3. ✅ 密钥未过期且未被禁用
4. ✅ 密钥有权限访问即梦 API
5. ✅ 即梦 API 服务已开通
6. ✅ 后端服务已重启

详细排查步骤请参考：[ACCESS_DENIED_FIX.md](#access-denied-错误)

### API 并发限制

即梦 API 有并发请求限制。如果遇到并发限制错误（50430），请：

1. 等待其他任务完成
2. 减少同时提交的任务数量
3. 实现任务队列机制

---

## 🗄️ 数据库配置

### Supabase 设置

#### 步骤 1: 创建 Supabase 项目

1. 访问 https://supabase.com
2. 使用 GitHub 账号登录
3. 创建新项目：
   - **Name**: jubianai
   - **Database Password**: 设置强密码（**记住这个密码！**）
   - **Region**: 选择最近的区域

#### 步骤 2: 获取连接字符串

1. 在 Supabase Dashboard 中
2. 进入 **Settings** → **Database**
3. 找到 **Connection Pooling** 部分
4. 选择 **Session mode**（推荐）或 **Transaction mode**
5. 复制连接字符串

**Session Pooler 连接字符串格式：**
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**重要提示：**
- 使用 `pooler.supabase.com`（不是 `supabase.co`）
- 端口是 `6543`（Session mode）或 `5432`（Transaction mode）
- 用户名格式：`postgres.[PROJECT-REF]`

#### 步骤 3: 初始化数据库表

1. 在 Supabase Dashboard 中
2. 点击 **SQL Editor**
3. 打开项目中的 `jubianai/supabase_init.sql` 文件
4. 复制所有 SQL 代码
5. 粘贴到 SQL Editor 中
6. 点击 **Run** 执行

#### 步骤 4: 配置环境变量

在 Render Dashboard 或部署环境中添加：

```bash
SUPABASE_DB_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**注意：** 将 `[PASSWORD]` 替换为你的实际数据库密码。

#### 步骤 5: 验证连接

部署后，检查 Render 日志，应该看到：
```
✅ 数据库连接成功
```

### 数据库连接问题（IPv6）

如果遇到 `Network is unreachable` 错误（IPv6 问题），解决方案：

1. **使用 Connection Pooling**（推荐）
   - 使用 `pooler.supabase.com` 主机
   - 端口使用 `6543`（Session mode）或 `5432`（Transaction mode）

2. **查找 Session Pooler**
   - Supabase Dashboard → Settings → Database → Connection Pooling
   - 选择 Session mode，复制连接字符串

3. **更新环境变量**
   - 在 Render 中更新 `SUPABASE_DB_URL`
   - 使用 Connection Pooling 连接字符串

### 重置数据库密码

如果不记得数据库密码：

1. Supabase Dashboard → Settings → Database
2. 找到 "Database password" 部分
3. 点击 "Reset database password"
4. 复制新密码
5. 更新连接字符串中的密码

---

## 🎬 功能说明

### 视频生成

#### 支持的分辨率

- **720P**: 1280x720（默认）
- **1080P**: 1920x1080

#### 支持的时长

- **5秒**: 121帧
- **10秒**: 241帧

#### req_key 说明

**720P:**
- 仅首帧: `jimeng_i2v_first_v30`
- 首尾帧: `i2v_first_tail_v30_jimeng`

**1080P:**
- 仅首帧: `jimeng_i2v_first_v30_1080`
- 首尾帧: `i2v_first_tail_v30_1080_jimeng`

### 视频增强功能

#### 超分辨率（提升分辨率）

支持将视频从 1080P 提升到 4K：

- **Real-ESRGAN**（默认）：通用场景，质量好
- **Waifu2x**：适合动漫风格

**使用方法：**
1. 在历史记录页面，鼠标悬停在视频上
2. 点击右下角的蓝色分辨率按钮
3. 选择 Real-ESRGAN 或 Waifu2x
4. 等待处理完成（通常需要几分钟）

**API 调用：**
```bash
POST /api/v1/video/history/{generation_id}/enhance-resolution
Content-Type: application/json

{
  "method": "real_esrgan",  # 或 "waifu2x"
  "scale": 2  # 放大倍数（2 = 2倍，1080P -> 4K）
}
```

#### 帧率提升（插帧）

支持将视频从 24fps 提升到 60fps：

- **RIFE**（默认）：快速，适合一般场景
- **FILM**：适合大运动/高遮挡场景，较慢

**智能切换：**
- 系统会自动检测视频是否有大运动
- 如果检测到大运动，自动切换到 FILM

**使用方法：**
1. 在历史记录页面，鼠标悬停在视频上
2. 点击右下角的绿色帧率按钮
3. 选择 RIFE（快速）或 FILM（大运动）
4. 如果选择 FILM，会提示处理时间较长

**API 调用：**
```bash
POST /api/v1/video/history/{generation_id}/enhance-fps
Content-Type: application/json

{
  "target_fps": 60,
  "method": "rife",  # 或 "film"
  "auto_switch": true  # 是否自动检测大运动并切换
}
```

#### 安装视频增强依赖

```bash
# 基础依赖
pip install opencv-python pillow numpy ffmpeg-python

# Real-ESRGAN
pip install realesrgan

# Waifu2x
pip install waifu2x

# RIFE
pip install rife

# FILM
pip install film

# TensorFlow Lite（用于加速）
pip install tensorflow-lite
```

**环境变量：**
```bash
# 启用 TensorFlow Lite 加速
USE_TFLITE=true
```

### 视频帧率和分辨率说明

#### 分辨率提升

**当前实现：**
- ✅ 720P 和 1080P 通过不同的 API 接口实现
- ✅ 更高分辨率（4K）需要使用超分辨率后处理

**提升方式：**
1. 等待即梦 API 提供新接口（推荐）
2. 使用 AI 超分辨率后处理（Real-ESRGAN / Waifu2x）

#### 帧率提升

**当前状态：**
- ⚠️ 即梦 API 不支持自定义帧率
- ⚠️ 输出帧率固定（通常是 24fps）

**提升方式：**
1. 等待即梦 API 支持自定义帧率（推荐）
2. 使用 AI 视频插帧后处理（RIFE / FILM）

---

## 🚢 部署指南

### Render 部署

#### 环境变量配置

在 Render Dashboard 中添加以下环境变量：

```bash
# 即梦 API
VOLCENGINE_ACCESS_KEY_ID=your_access_key_id
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_access_key

# Supabase 数据库
SUPABASE_DB_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# 默认用户 API Key
DEFAULT_API_KEY=default_key

# 对象存储（可选）
STORAGE_TYPE=aliyun_oss
ALIYUN_OSS_ACCESS_KEY_ID=your_key
ALIYUN_OSS_ACCESS_KEY_SECRET=your_secret
ALIYUN_OSS_BUCKET_NAME=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

#### 更新环境变量步骤

1. 访问 Render Dashboard
2. 进入你的服务
3. 点击 **Environment** 标签
4. 找到要更新的环境变量
5. 点击编辑图标
6. 更新值
7. 点击 **Save**
8. 服务会自动重新部署

#### 验证部署

1. 查看 Render 日志，确认服务正常启动
2. 访问健康检查端点：`https://your-service.onrender.com/health`
3. 应该返回：`{"status": "healthy"}`

---

## 🐛 故障排除

### Access Denied 错误

**错误信息：**
```
50400 Access Denied: Access Denied
```

**解决步骤：**

1. **检查环境变量**
   - 确认 `VOLCENGINE_ACCESS_KEY_ID` 和 `VOLCENGINE_SECRET_ACCESS_KEY` 已设置
   - 确认密钥值正确（无多余空格）

2. **验证 API 密钥**
   - 登录火山引擎控制台
   - 检查密钥是否过期或被禁用
   - 确认密钥有权限访问即梦 API

3. **检查服务状态**
   - 确认即梦 API 服务已开通
   - 检查账户余额

4. **重启服务**
   - 环境变量更改后需要重启服务

### 数据库连接失败

**错误信息：**
```
Network is unreachable (IPv6)
```

**解决方案：**

1. **使用 Connection Pooling**
   - 使用 `pooler.supabase.com` 主机
   - 端口使用 `6543`（Session mode）

2. **更新连接字符串**
   - 在 Supabase Dashboard 中获取 Connection Pooling 连接字符串
   - 更新 Render 环境变量 `SUPABASE_DB_URL`

3. **验证连接**
   - 检查 Render 日志，应该看到 "✅ 数据库连接成功"

### 视频生成超时

**问题：** 视频生成任务长时间显示"生成中"

**解决方案：**

1. **检查任务状态**
   - 系统会自动检测超时任务（超过10分钟）
   - 超时任务会自动标记为失败

2. **重新生成**
   - 如果任务超时，可以重新生成视频

3. **检查 API 状态**
   - 确认即梦 API 服务正常
   - 检查是否有并发限制

### 视频增强失败

**问题：** 超分辨率或插帧处理失败

**解决方案：**

1. **检查依赖**
   - 确认已安装所有必需的 Python 包
   - 确认模型文件已下载

2. **检查资源**
   - 确认服务器有足够的 CPU/GPU 资源
   - 确认有足够的存储空间

3. **查看日志**
   - 检查后端日志中的详细错误信息

### 配额耗尽

**错误信息：**
```
Quota Exhausted
```

**解决方案：**

1. **检查配额**
   - 登录火山引擎控制台
   - 查看即梦 API 使用情况

2. **升级套餐**
   - 购买更多配额
   - 或等待配额重置

---

## 📝 API 文档

### 视频生成

```bash
POST /api/v1/video/generate
Content-Type: application/json

{
  "prompt": "视频描述",
  "duration": 5,
  "fps": 24,
  "width": 1280,
  "height": 720,
  "resolution": "720p",  # 或 "1080p"
  "first_frame": "base64_image_data",  # 可选
  "last_frame": "base64_image_data"    # 可选
}
```

### 查询任务状态

```bash
GET /api/v1/video/status/{task_id}
```

### 获取历史记录

```bash
GET /api/v1/video/history?limit=20&offset=0
```

### 视频增强

```bash
# 提升分辨率
POST /api/v1/video/history/{generation_id}/enhance-resolution

# 提升帧率
POST /api/v1/video/history/{generation_id}/enhance-fps
```

---

## 🔗 相关链接

- [即梦 API 文档](https://www.volcengine.com/docs/85621?lang=zh)
- [火山引擎控制台](https://console.volcengine.com/)
- [Supabase 文档](https://supabase.com/docs)
- [Render 文档](https://render.com/docs)

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新：** 2025-12-25

