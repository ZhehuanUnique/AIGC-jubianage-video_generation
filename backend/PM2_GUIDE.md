# PM2 后端服务管理指南

PM2 是一个强大的 Node.js 进程管理器，也可以用来管理 Python 应用。它提供了自动重启、日志管理、监控等功能。

## 安装 PM2

### 前提条件

需要先安装 Node.js 和 npm：

1. 下载 Node.js：https://nodejs.org/
2. 安装完成后，打开命令行验证：
   ```cmd
   node --version
   npm --version
   ```

### 安装 PM2

```cmd
npm install -g pm2
```

验证安装：
```cmd
pm2 --version
```

## 快速开始

### 1. 启动服务

**方法 1：使用批处理脚本（推荐）**
```cmd
backend\pm2_start.bat
```

**方法 2：手动启动**
```cmd
cd backend
pm2 start ecosystem.config.cjs
```

### 2. 查看服务状态

```cmd
pm2 status
```

输出示例：
```
┌─────┬──────────────┬─────────┬─────────┬──────────┬─────────┐
│ id  │ name         │ mode    │ ↺       │ status   │ cpu     │
├─────┼──────────────┼─────────┼─────────┼──────────┼─────────┤
│ 0   │ aigc-backend │ fork    │ 0       │ online   │ 0%      │
└─────┴──────────────┴─────────┴─────────┴──────────┴─────────┘
```

### 3. 查看日志

```cmd
# 查看实时日志
pm2 logs aigc-backend

# 查看最近 100 行日志
pm2 logs aigc-backend --lines 100

# 清空日志
pm2 flush
```

### 4. 停止服务

```cmd
backend\pm2_stop.bat
```

或手动：
```cmd
pm2 stop aigc-backend
```

### 5. 重启服务

```cmd
backend\pm2_restart.bat
```

或手动：
```cmd
pm2 restart aigc-backend
```

### 6. 删除服务

```cmd
backend\pm2_delete.bat
```

或手动：
```cmd
pm2 delete aigc-backend
```

## 设置开机自启动

### 自动设置（推荐）

1. **以管理员身份运行** `pm2_setup_autostart.bat`
   - 右键文件 → 选择"以管理员身份运行"
   - 脚本会自动保存配置并生成启动脚本

2. **手动设置**

```cmd
# 1. 保存当前进程列表
pm2 save

# 2. 生成开机自启动脚本（需要管理员权限）
pm2 startup

# 3. 复制输出的命令并执行（PM2 会输出类似这样的命令）
# 例如：pm2 startup systemd -u Administrator --hp C:\Users\Administrator
```

### 禁用开机自启动

```cmd
pm2 unstartup
```

## 常用命令

### 进程管理

```cmd
# 启动服务
pm2 start ecosystem.config.cjs

# 停止服务
pm2 stop aigc-backend

# 重启服务
pm2 restart aigc-backend

# 删除服务
pm2 delete aigc-backend

# 查看所有进程
pm2 list

# 查看详细信息
pm2 show aigc-backend
```

### 日志管理

```cmd
# 查看实时日志
pm2 logs aigc-backend

# 查看所有日志
pm2 logs

# 查看错误日志
pm2 logs aigc-backend --err

# 查看输出日志
pm2 logs aigc-backend --out

# 清空所有日志
pm2 flush

# 重载日志（日志文件会重新创建）
pm2 reloadLogs
```

### 监控

```cmd
# 实时监控（CPU、内存使用情况）
pm2 monit

# 查看进程信息
pm2 info aigc-backend
```

### 配置管理

```cmd
# 保存当前进程列表
pm2 save

# 恢复保存的进程列表
pm2 resurrect

# 删除保存的进程列表
pm2 kill
```

## 配置文件说明

`ecosystem.config.cjs` 配置文件说明（注意：使用 `.cjs` 扩展名以避免 ES 模块问题）：

```javascript
module.exports = {
  apps: [{
    name: 'aigc-backend',              // 进程名称
    script: 'python',                   // 解释器
    args: '-m uvicorn backend.api:app --host 0.0.0.0 --port 8001',  // 启动参数
    cwd: '...',                         // 工作目录（需要修改为你的实际路径）
    interpreter: 'python',              // Python 解释器
    instances: 1,                       // 实例数量（1 = 单实例）
    autorestart: true,                  // 自动重启
    watch: false,                       // 是否监听文件变化（开发环境可设为 true）
    max_memory_restart: '1G',          // 内存超过 1G 自动重启
    env: {                              // 环境变量
      NODE_ENV: 'production',
      PORT: '8001'
    },
    error_file: './logs/pm2-error.log', // 错误日志路径
    out_file: './logs/pm2-out.log',     // 输出日志路径
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',  // 日志时间格式
    merge_logs: true,                   // 合并日志
    time: true                          // 日志中显示时间
  }]
}
```

### 修改工作目录

如果项目路径不同，需要修改 `ecosystem.config.js` 中的 `cwd` 字段：

```javascript
cwd: 'C:\\你的\\实际\\项目\\路径\\backend',
```

## 高级功能

### 集群模式（多实例）

如果需要运行多个实例以提高性能：

```javascript
instances: 4,  // 运行 4 个实例
exec_mode: 'cluster'  // 集群模式
```

**注意**：对于 Python 应用，通常使用单实例模式。

### 环境变量

可以在配置文件中设置不同的环境变量：

```javascript
env: {
  NODE_ENV: 'production',
  PORT: '8001'
},
env_development: {
  NODE_ENV: 'development',
  PORT: '8001',
  watch: true  // 开发环境启用文件监听
}
```

启动时指定环境：
```cmd
pm2 start ecosystem.config.cjs --env development
```

### 自动重启策略

```javascript
autorestart: true,           // 自动重启
max_restarts: 10,             // 最大重启次数
min_uptime: '10s',           // 最小运行时间
restart_delay: 4000,         // 重启延迟（毫秒）
```

## 故障排查

### 服务无法启动

1. **检查 Python 路径**
   ```cmd
   python --version
   ```

2. **检查工作目录**
   - 确保 `ecosystem.config.js` 中的 `cwd` 路径正确

3. **查看错误日志**
   ```cmd
   pm2 logs aigc-backend --err
   ```

4. **手动测试启动**
   ```cmd
   cd backend
   python -m uvicorn backend.api:app --host 0.0.0.0 --port 8001
   ```

5. **检查配置文件**
   - 确保使用 `ecosystem.config.cjs`（不是 `.js`）
   - 检查 `cwd` 路径是否正确

### 服务频繁重启

1. **查看日志找出原因**
   ```cmd
   pm2 logs aigc-backend --lines 50
   ```

2. **检查内存使用**
   ```cmd
   pm2 monit
   ```

3. **调整内存限制**
   ```javascript
   max_memory_restart: '2G'  // 增加到 2G
   ```

### 端口被占用

```cmd
# 检查端口占用
netstat -ano | findstr :8001

# 如果被占用，可以：
# 1. 关闭占用端口的进程
# 2. 或修改配置文件中的端口
```

### PM2 命令不识别

确保 PM2 已全局安装：
```cmd
npm install -g pm2
```

如果还是不行，检查 npm 全局路径是否在 PATH 中。

## 与任务计划程序对比

| 特性 | PM2 | 任务计划程序 |
|------|-----|------------|
| 自动重启 | ✅ | ❌ |
| 日志管理 | ✅ 强大 | ⚠️ 基础 |
| 监控功能 | ✅ | ❌ |
| 集群模式 | ✅ | ❌ |
| 内存限制 | ✅ | ❌ |
| 需要 Node.js | ✅ | ❌ |
| 系统自带 | ❌ | ✅ |

## 推荐使用场景

- ✅ **开发环境**：需要自动重启、日志管理
- ✅ **生产环境**：需要监控、自动恢复
- ✅ **需要多实例**：负载均衡
- ❌ **简单场景**：只需要开机启动，不需要其他功能

## 卸载 PM2

```cmd
npm uninstall -g pm2
```

删除保存的配置：
```cmd
pm2 kill
pm2 unstartup
```

## 相关文件

- `ecosystem.config.cjs` - PM2 配置文件（使用 .cjs 扩展名）
- `pm2_start.bat` - 启动脚本
- `pm2_stop.bat` - 停止脚本
- `pm2_restart.bat` - 重启脚本
- `pm2_delete.bat` - 删除脚本
- `pm2_setup_autostart.bat` - 设置开机自启动脚本
- `logs/` - 日志目录（自动创建）

## 更多资源

- PM2 官方文档：https://pm2.keymetrics.io/
- PM2 GitHub：https://github.com/Unitech/pm2

