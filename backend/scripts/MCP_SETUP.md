# MCP 服务配置说明

本文档说明如何配置 MCP（Model Context Protocol）服务来修复历史记录。

## 已配置的 MCP 服务

### 1. Vercel MCP

**配置信息：**
- Command: `npx`
- Args: `["-y", "@robinson_ai_systems/vercel-mcp"]`
- Environment Variable: `VERCEL_TOKEN=bUFnjiVqrAvBYZyTmED7Q9wl`

**用途：** 获取 Vercel 部署信息，可能包含视频文件的 URL。

### 2. Supabase MCP

**配置信息：**
- Command: `cmd /c npx -y @supabase/mcp-server-supabase@latest --project-ref=sggdokxjqycskeybyqvv`
- Environment Variable: `SUPABASE_ACCESS_TOKEN=sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03`
- Project Ref: `sggdokxjqycskeybyqvv`

**用途：** 直接从 Supabase 数据库获取历史记录数据。

### 3. Render MCP（待查找）

如果存在 Render MCP，请添加配置。

## 环境变量配置

在 `backend/.env` 文件中添加以下配置：

```env
# Supabase MCP 配置
SUPABASE_PROJECT_REF=sggdokxjqycskeybyqvv
SUPABASE_ACCESS_TOKEN=sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03

# Vercel MCP 配置
VERCEL_TOKEN=bUFnjiVqrAvBYZyTmED7Q9wl

# Render MCP 配置（如果存在）
# RENDER_API_KEY=your_render_api_key
```

## 使用方法

运行修复脚本：

```bash
cd backend
python scripts/fix_history_from_mcp.py
```

脚本会：
1. 从 Supabase MCP 获取历史记录数据
2. 从 Vercel MCP 获取部署信息
3. 将数据同步到本地数据库

## 注意事项

1. 确保数据库连接正常（`SUPABASE_DB_URL` 已配置）
2. 确保 MCP 服务的 Token 有效
3. 脚本会跳过已存在的记录，只更新或新增缺失的记录

