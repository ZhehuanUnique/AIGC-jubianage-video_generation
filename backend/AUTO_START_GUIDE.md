# 后端服务自动启动指南

本指南提供了多种方式让后端服务器在 Windows 系统上自动启动。

## 方案 1：Windows 任务计划程序（推荐）

### 自动安装（推荐）

1. **以管理员身份运行** `install_backend_service.bat`
   - 右键点击文件 → 选择"以管理员身份运行"
   - 脚本会自动创建开机自启动任务

2. **验证安装**
   ```cmd
   schtasks /query /tn "AIGC_Backend_Service"
   ```

3. **手动运行任务**（测试）
   ```cmd
   schtasks /run /tn "AIGC_Backend_Service"
   ```

4. **卸载服务**
   - 以管理员身份运行 `uninstall_backend_service.bat`

### 手动安装

1. 打开"任务计划程序"（Task Scheduler）
   - 按 `Win + R`，输入 `taskschd.msc`，回车

2. 创建基本任务
   - 右侧点击"创建基本任务"
   - 名称：`AIGC_Backend_Service`
   - 描述：`剧变时代 - AI 视频生成后端服务`

3. 设置触发器
   - 选择"当计算机启动时"

4. 设置操作
   - 选择"启动程序"
   - 程序或脚本：浏览选择 `backend\start_backend_service.bat`
   - 起始于：`C:\Users\Administrator\Desktop\AIGC-jubianage-video_generation\backend`

5. 完成设置
   - 勾选"当单击完成时，打开此任务属性的对话框"
   - 在"常规"标签页中：
     - 勾选"不管用户是否登录都要运行"
     - 勾选"使用最高权限运行"
     - 配置：选择"Windows 10"或"Windows Server 2016"

6. 保存并测试
   - 点击"确定"
   - 右键任务 → "运行" 测试是否正常启动

## 方案 2：开机自启动文件夹

1. 按 `Win + R`，输入 `shell:startup`，回车
   - 这会打开启动文件夹

2. 创建快捷方式
   - 右键 `backend\start_backend_service.bat`
   - 选择"创建快捷方式"
   - 将快捷方式移动到启动文件夹

3. 设置快捷方式属性
   - 右键快捷方式 → "属性"
   - "起始位置"设置为：`C:\Users\Administrator\Desktop\AIGC-jubianage-video_generation\backend`
   - "运行方式"选择"最小化"

**注意**：此方法会在用户登录时启动，如果用户未登录则不会启动。

## 方案 3：使用 NSSM（Windows 服务管理器）

NSSM 可以将任何程序注册为 Windows 服务，更稳定可靠。

### 安装 NSSM

1. 下载 NSSM
   - 访问：https://nssm.cc/download
   - 下载最新版本（推荐 64 位版本）

2. 解压到项目目录
   - 例如：`C:\Users\Administrator\Desktop\AIGC-jubianage-video_generation\backend\nssm`

### 注册服务

1. 以管理员身份打开 PowerShell 或 CMD

2. 进入 NSSM 目录
   ```cmd
   cd C:\Users\Administrator\Desktop\AIGC-jubianage-video_generation\backend\nssm\win64
   ```

3. 安装服务
   ```cmd
   nssm install AIGC_Backend_Service
   ```

4. 在弹出的 GUI 中配置：
   - **Application** 标签：
     - Path: `C:\Python\python.exe`（你的 Python 路径）
     - Startup directory: `C:\Users\Administrator\Desktop\AIGC-jubianage-video_generation\backend`
     - Arguments: `-m uvicorn backend.api:app --host 0.0.0.0 --port 8001`
   
   - **Details** 标签：
     - Display name: `AIGC Backend Service`
     - Description: `剧变时代 - AI 视频生成后端服务`
   
   - **Log on** 标签：
     - 选择"Local System account"
     - 勾选"Allow service to interact with desktop"（可选）

5. 点击"Install service"

### 管理服务

```cmd
# 启动服务
nssm start AIGC_Backend_Service

# 停止服务
nssm stop AIGC_Backend_Service

# 重启服务
nssm restart AIGC_Backend_Service

# 查看服务状态
nssm status AIGC_Backend_Service

# 删除服务
nssm remove AIGC_Backend_Service confirm
```

## 方案 4：使用 PM2（Node.js 进程管理器）

虽然 PM2 主要用于 Node.js，但也可以管理 Python 进程。

### 安装 PM2

```cmd
npm install -g pm2
```

### 创建配置文件

创建 `backend/ecosystem.config.js`：

```javascript
module.exports = {
  apps: [{
    name: 'aigc-backend',
    script: 'python',
    args: '-m uvicorn backend.api:app --host 0.0.0.0 --port 8001',
    cwd: 'C:\\Users\\Administrator\\Desktop\\AIGC-jubianage-video_generation\\backend',
    interpreter: 'python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
```

### 使用 PM2

```cmd
# 启动
pm2 start ecosystem.config.js

# 保存当前进程列表（开机自启动）
pm2 save
pm2 startup

# 查看状态
pm2 status

# 查看日志
pm2 logs aigc-backend

# 停止
pm2 stop aigc-backend

# 删除
pm2 delete aigc-backend
```

## 推荐方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 任务计划程序 | 系统自带，无需额外软件 | 需要管理员权限 | ⭐⭐⭐⭐⭐ |
| 启动文件夹 | 简单，无需权限 | 需要用户登录 | ⭐⭐⭐ |
| NSSM | 稳定，专业 | 需要下载软件 | ⭐⭐⭐⭐ |
| PM2 | 功能强大，自动重启 | 需要 Node.js | ⭐⭐⭐ |

## 验证服务运行

无论使用哪种方案，都可以通过以下方式验证：

1. **检查端口**
   ```cmd
   netstat -ano | findstr :8001
   ```

2. **访问 API**
   - 浏览器打开：http://localhost:8001/docs
   - 应该能看到 FastAPI 的 Swagger 文档

3. **查看日志**
   - 任务计划程序：在任务属性中查看"历史记录"
   - NSSM：查看服务日志
   - PM2：使用 `pm2 logs`

## 故障排查

### 服务无法启动

1. 检查 Python 路径是否正确
2. 检查工作目录是否正确
3. 检查端口 8001 是否被占用
4. 查看错误日志

### 服务启动后立即退出

1. 检查 `.env` 文件配置是否正确
2. 检查数据库连接是否正常
3. 查看详细错误日志

### 权限问题

- 确保以管理员身份运行安装脚本
- 检查任务计划程序的运行权限设置

## 注意事项

1. **环境变量**：确保 `.env` 文件中的配置正确
2. **Python 路径**：如果使用虚拟环境，需要修改启动脚本中的 Python 路径
3. **防火墙**：确保 Windows 防火墙允许 8001 端口
4. **自动重启**：如果服务崩溃，任务计划程序不会自动重启，建议使用 NSSM 或 PM2

