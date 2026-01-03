# 历史记录修复脚本

## 功能说明

`fix_history_from_mcp.py` 脚本用于从 MCP（Model Context Protocol）服务获取数据并修复历史记录。

## 支持的 MCP 服务

### 1. Supabase MCP ✅
- 从 Supabase 数据库直接获取历史记录
- 自动同步到本地数据库
- 支持新增和更新记录

### 2. Vercel MCP ✅
- 获取 Vercel 部署信息
- 可用于查找视频文件的 URL

### 3. Render API ⚠️
- Render 目前没有官方的 MCP 支持
- 使用 Render REST API 获取服务信息
- 需要配置 `RENDER_API_KEY`
- 获取方法：参见 `RENDER_API_KEY_GUIDE.md`

## 使用方法

### 1. 配置环境变量

在 `backend/.env` 文件中添加：

```env
# Supabase MCP 配置
SUPABASE_PROJECT_REF=sggdokxjqycskeybyqvv
SUPABASE_ACCESS_TOKEN=sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03

# Vercel MCP 配置
VERCEL_TOKEN=bUFnjiVqrAvBYZyTmED7Q9wl

# Render API 配置（可选）
RENDER_API_KEY=your_render_api_key
```

### 2. 运行脚本

```bash
cd backend
python scripts/fix_history_from_mcp.py
```

## 脚本功能

1. **从 Supabase 获取数据**
   - 通过 Supabase REST API 获取所有历史记录
   - 自动同步到本地数据库
   - 跳过已存在的记录，只更新或新增

2. **从 Vercel 获取部署信息**
   - 获取所有部署列表
   - 可用于查找视频文件的 URL

3. **从 Render 获取服务信息**
   - 获取所有服务列表
   - 可用于查找后端服务的 URL

## 注意事项

1. 确保数据库连接正常（`SUPABASE_DB_URL` 已配置）
2. 确保 MCP 服务的 Token 有效
3. 脚本会跳过已存在的记录，只更新或新增缺失的记录
4. 建议在运行前备份数据库

## 故障排除

### 数据库连接失败
- 检查 `SUPABASE_DB_URL` 环境变量是否正确
- 确认数据库服务是否正常运行

### Supabase API 调用失败
- 检查 `SUPABASE_ACCESS_TOKEN` 是否有效
- 确认 `SUPABASE_PROJECT_REF` 是否正确

### Vercel API 调用失败
- 检查 `VERCEL_TOKEN` 是否有效
- 确认 Token 是否有足够的权限

