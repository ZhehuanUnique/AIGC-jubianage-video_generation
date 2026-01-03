# Render API Key 获取指南

## 获取步骤

### 1. 登录 Render 仪表板

访问 [Render Dashboard](https://dashboard.render.com/) 并使用您的账户登录。

### 2. 进入账户设置（方法一）

1. 在仪表板的**右上角**，点击您的**头像**或**用户名**
2. 在下拉菜单中选择 **"Account Settings"**（账户设置）或 **"Settings"**（设置）
3. 在设置页面中查找 **"API Keys"** 或 **"API"** 部分

### 2. 进入工作区设置（方法二）

如果方法一找不到，尝试以下步骤：

1. 点击左侧导航栏中的 **"Settings"**（设置）图标（齿轮图标）
2. 在设置页面中查找 **"API Keys"** 或 **"API"** 部分

### 3. 创建 API 密钥

1. 找到 **"API Keys"** 部分后，点击 **"Create API Key"** 或 **"Generate New API Key"** 按钮
2. 系统会提示您输入 API Key 的名称（可选，用于标识这个密钥的用途）
3. 点击确认后，系统将生成一个新的 API 密钥

### ⚠️ 如果找不到 API Keys 选项

可能的原因和解决方案：

1. **需要升级到付费计划**
   - 某些 Render 功能可能需要 Professional 计划
   - 检查您的账户类型

2. **权限不足**
   - 确保您有工作区的管理员权限
   - 联系工作区所有者获取权限

3. **界面更新**
   - Render 可能更新了界面
   - 尝试在搜索框中搜索 "API" 或 "API Key"

4. **直接访问 API 文档**
   - 访问 [Render API 文档](https://api-docs.render.com/reference/authentication)
   - 查看最新的获取方法

### 4. 保存 API 密钥

⚠️ **重要提示：**
- API 密钥**只会显示一次**
- 请立即复制并安全地保存该密钥
- 如果关闭页面后忘记密钥，需要重新创建

### 5. 配置到项目中

将获取到的 API Key 添加到 `backend/.env` 文件中：

```env
# Render API 配置
RENDER_API_KEY=your_render_api_key_here
```

## 使用 API Key

在 HTTP 请求中使用 API Key 时，需要在请求头中包含：

```
Authorization: Bearer YOUR_API_KEY
```

## 安全注意事项

1. **不要将 API Key 提交到 Git 仓库**
   - 确保 `.env` 文件在 `.gitignore` 中
   - 不要在代码中硬编码 API Key

2. **API Key 权限**
   - API Key 可以访问您所有工作区的资源
   - 请妥善保管，避免泄露

3. **如果密钥泄露**
   - 立即在 Render Dashboard 中撤销该密钥
   - 创建新的 API Key 替换

## 验证 API Key

您可以使用以下命令测试 API Key 是否有效：

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.render.com/v1/services
```

如果返回服务列表，说明 API Key 配置正确。

## 替代方案：使用 Personal Access Token

如果找不到 API Key 选项，Render 可能使用 **Personal Access Token** 替代：

### 获取 Personal Access Token

1. 登录 Render Dashboard
2. 点击右上角头像 → **"Account Settings"**
3. 查找 **"Personal Access Tokens"** 或 **"Tokens"** 部分
4. 点击 **"Create Token"** 或 **"Generate Token"**
5. 输入名称并创建
6. 复制生成的 Token（只会显示一次）

### 使用 Personal Access Token

Personal Access Token 的使用方式与 API Key 相同：

```env
# Render API 配置（使用 Personal Access Token）
RENDER_API_KEY=your_personal_access_token_here
```

## 直接访问链接

如果上述方法都找不到，可以尝试直接访问：

- **账户设置**: `https://dashboard.render.com/account`
- **API 文档**: `https://api-docs.render.com/`
- **认证文档**: `https://api-docs.render.com/reference/authentication`

## 联系支持

如果仍然找不到，可以：

1. 点击 Render Dashboard 左下角的 **"Contact support"**（联系支持）
2. 询问如何获取 API Key 或 Personal Access Token
3. 说明您需要使用 Render API 来管理服务

## 相关链接

- [Render API 文档](https://api-docs.render.com/)
- [Render 认证文档](https://api-docs.render.com/reference/authentication)
- [Render Dashboard](https://dashboard.render.com/)

