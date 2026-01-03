# Cursor MCP 服务器配置指南

## 问题说明

在 Cursor 的 **Tools & MCP** 设置页面中，需要通过 UI 手动添加 MCP 服务器，而不是仅使用配置文件。

## 配置步骤

### 1. 打开 Cursor Settings

- 点击左下角齿轮图标 ⚙️
- 或使用快捷键 `Ctrl+,`
- 或菜单：**File** → **Preferences** → **Settings**

### 2. 进入 Tools & MCP 页面

- 在左侧导航栏找到 **"Tools & MCP"**（扳手和齿轮图标）
- 点击进入

### 3. 添加 Supabase MCP 服务器

点击 **"New MCP Server"** 按钮，然后填写：

**服务器名称：**
```
supabase-jubianai
```

**命令 (Command)：**
```
cmd
```

**参数 (Args)** - 每行一个参数：
```
/c
npx
-y
@supabase/mcp-server-supabase@latest
--project-ref=sggdokxjqycskeybyqvv
```

**环境变量 (Environment Variables)：**
- Key: `SUPABASE_ACCESS_TOKEN`
- Value: `sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03`

### 4. 添加 Vercel MCP 服务器

再次点击 **"New MCP Server"**，填写：

**服务器名称：**
```
vercel
```

**命令 (Command)：**
```
npx
```

**参数 (Args)** - 每行一个参数：
```
-y
@robinson_ai_systems/vercel-mcp
```

**环境变量 (Environment Variables)：**
- Key: `VERCEL_TOKEN`
- Value: `bUFnjiVqrAvBYZyTmED7Q9wl`

### 5. 保存并重启

- 保存配置
- 重启 Cursor
- 在 **Tools & MCP** 页面应该能看到新添加的服务器

## 配置格式说明

### Supabase MCP 完整配置

```json
{
  "name": "supabase-jubianai",
  "command": "cmd",
  "args": [
    "/c",
    "npx",
    "-y",
    "@supabase/mcp-server-supabase@latest",
    "--project-ref=sggdokxjqycskeybyqvv"
  ],
  "env": {
    "SUPABASE_ACCESS_TOKEN": "sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03"
  }
}
```

### Vercel MCP 完整配置

```json
{
  "name": "vercel",
  "command": "npx",
  "args": [
    "-y",
    "@robinson_ai_systems/vercel-mcp"
  ],
  "env": {
    "VERCEL_TOKEN": "bUFnjiVqrAvBYZyTmED7Q9wl"
  }
}
```

## 验证配置

配置完成后：

1. **检查服务器状态**
   - 在 **Tools & MCP** 页面，服务器应该显示为绿色（已启用）
   - 如果显示红色，点击查看错误信息

2. **测试连接**
   - 服务器启动后，应该能看到可用的工具数量
   - 例如：Supabase MCP 可能显示 "X tools enabled"

3. **使用 MCP 功能**
   - 在聊天中，可以尝试使用 MCP 提供的工具
   - 例如：查询 Supabase 数据、管理 Vercel 部署等

## 故障排除

### 如果服务器无法启动

1. **检查 Node.js 是否安装**
   ```bash
   node --version
   npx --version
   ```

2. **检查网络连接**
   - 确保可以访问 npm registry
   - 可能需要配置代理

3. **查看错误日志**
   - 在 Cursor 中查看 MCP 服务器的错误信息
   - 检查环境变量是否正确

### 如果看不到服务器

1. **刷新页面**
   - 在 **Tools & MCP** 页面刷新

2. **重启 Cursor**
   - 完全关闭并重新打开 Cursor

3. **检查配置格式**
   - 确保所有参数都正确填写
   - 特别注意参数之间的换行

## 项目配置文件

项目根目录的 `mcp.json` 文件已创建，包含所有配置信息，可以作为参考。

## 相关资源

- Supabase MCP: https://github.com/supabase/mcp-server-supabase
- Vercel MCP: https://github.com/robinson-ai-systems/vercel-mcp
- MCP 协议: https://modelcontextprotocol.io/
