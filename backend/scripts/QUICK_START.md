# 快速开始 - 修复历史记录

## ✅ API Key 验证成功

Render API Key 已验证可用！

## 配置步骤

### 1. 更新 .env 文件

在 `backend/.env` 文件中添加或更新以下配置：

```env
# MCP 服务配置（用于修复历史记录）

# Supabase MCP 配置
SUPABASE_PROJECT_REF=sggdokxjqycskeybyqvv
SUPABASE_ACCESS_TOKEN=sbp_55d3bff12a73fad53040ea5b2db387d0d84a2e03

# Vercel MCP 配置
VERCEL_TOKEN=bUFnjiVqrAvBYZyTmED7Q9wl

# Render API 配置
RENDER_API_KEY=rnd_QtPtywDxKnQAUCABtvIwBiwf0lvX
```

### 2. 运行修复脚本

```bash
cd backend
python scripts/fix_history_from_mcp.py
```

## 脚本功能

脚本会：
1. ✅ 从 Supabase 获取所有历史记录
2. ✅ 从 Vercel 获取部署信息
3. ✅ 从 Render 获取服务信息
4. ✅ 自动同步数据到本地数据库

## 预期输出

```
🚀 开始从 MCP 服务修复历史记录...

📡 尝试从 Supabase MCP 获取数据...
✅ 从 Supabase 获取到 X 条记录

📡 尝试从 Vercel MCP 获取数据...
✅ 从 Vercel 获取到 X 个部署

📡 尝试从 Render API 获取数据...
✅ 从 Render 获取到 X 个服务

🔄 开始同步 X 条记录到数据库...
  ✅ 同步新记录: task_id_xxx
  ✅ 更新记录: task_id_yyy

📊 同步完成:
  - 新增: X 条
  - 更新: Y 条
  - 跳过: Z 条

✅ 历史记录修复完成！
```

## 注意事项

1. 确保数据库连接正常（`SUPABASE_DB_URL` 已配置）
2. 脚本会跳过已存在的记录，只更新或新增缺失的记录
3. 建议在运行前备份数据库

