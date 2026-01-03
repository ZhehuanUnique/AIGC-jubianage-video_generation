# 数据库配置说明

## 当前状态

修复脚本已运行，但需要配置 `SUPABASE_DB_URL` 环境变量才能同步历史记录。

## 配置步骤

### 1. 获取 Supabase 数据库连接字符串

根据您的 MCP 配置，Supabase 项目信息：
- **Project Ref**: `sggdokxjqycskeybyqvv`
- **Access Token**: 已配置

#### 方法 1：使用 Connection Pooling（推荐）

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择项目（Project Ref: sggdokxjqycskeybyqvv）
3. 进入 **Settings** → **Database**
4. 找到 **Connection Pooling** 部分
5. 选择 **Session mode**（推荐）
6. 复制连接字符串

**连接字符串格式：**
```
postgresql://postgres.sggdokxjqycskeybyqvv:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

#### 方法 2：使用直接连接

1. 在 Supabase Dashboard 中
2. 进入 **Settings** → **Database**
3. 找到 **Connection string** 部分
4. 选择 **URI** 格式
5. 复制连接字符串

**连接字符串格式：**
```
postgresql://postgres:[PASSWORD]@db.sggdokxjqycskeybyqvv.supabase.co:5432/postgres
```

### 2. 配置到 .env 文件

在 `backend/.env` 文件中添加：

```env
# Supabase 数据库配置
SUPABASE_DB_URL=postgresql://postgres.sggdokxjqycskeybyqvv:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**重要提示：**
- 将 `[YOUR-PASSWORD]` 替换为您的数据库密码
- 将 `[REGION]` 替换为您的区域（如：ap-southeast-1）
- 如果使用直接连接，格式会有所不同

### 3. 重新运行修复脚本

配置完成后，重新运行：

```bash
cd backend
python scripts/fix_history_from_mcp.py
```

## 如果不知道数据库密码

1. 访问 Supabase Dashboard
2. 进入 **Settings** → **Database**
3. 找到 **Database password** 部分
4. 如果忘记了密码，可以点击 **"Reset database password"** 重置
5. **重要**：重置后需要更新所有使用该密码的地方

## 验证数据库连接

配置完成后，可以运行以下命令测试连接：

```bash
cd backend
python -c "from backend.database import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT 1')); print('数据库连接成功！')"
```

如果看到 "数据库连接成功！"，说明配置正确。

