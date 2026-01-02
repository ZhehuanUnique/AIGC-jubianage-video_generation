-- Supabase 数据库初始化脚本
-- 在 Supabase Dashboard 的 SQL Editor 中执行此脚本

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);

-- 2. 创建视频生成历史表
CREATE TABLE IF NOT EXISTS video_generations (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- 生成参数
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    duration INTEGER NOT NULL,
    fps INTEGER DEFAULT 24,
    width INTEGER DEFAULT 720,
    height INTEGER DEFAULT 720,
    seed INTEGER,
    
    -- 首尾帧
    first_frame_url TEXT,
    last_frame_url TEXT,
    
    -- 视频信息
    video_url TEXT,
    video_name VARCHAR(255),
    video_size INTEGER,
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- 扩展元数据
    metadata JSONB,
    
    -- 用户操作标记
    is_ultra_hd BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_liked BOOLEAN DEFAULT FALSE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_video_generations_task_id ON video_generations(task_id);
CREATE INDEX IF NOT EXISTS idx_video_generations_user_id ON video_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_video_generations_status ON video_generations(status);
CREATE INDEX IF NOT EXISTS idx_video_generations_created_at ON video_generations(created_at DESC);

-- 3. 创建资产管理表（可选，如果还没有）
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    character_name VARCHAR(100),
    view_type VARCHAR(50),
    category VARCHAR(50),
    tags TEXT[],
    uploaded_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_assets_character_name ON assets(character_name);
CREATE INDEX IF NOT EXISTS idx_assets_view_type ON assets(view_type);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category);
CREATE INDEX IF NOT EXISTS idx_assets_user_id ON assets(user_id);

-- 4. 创建知识库表（可选，未来扩展）
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT,
    file_type VARCHAR(50),
    characters TEXT[],
    scenes JSONB,
    vector_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_knowledge_base_title ON knowledge_base(title);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_characters ON knowledge_base USING GIN(characters);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_vector_id ON knowledge_base(vector_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_user_id ON knowledge_base(user_id);

-- 5. 插入默认用户（可选）
-- 如果使用单用户模式，可以创建一个默认用户
INSERT INTO users (username, api_key, is_active)
VALUES ('default_user', 'default_key', TRUE)
ON CONFLICT (username) DO NOTHING;

-- 6. 启用 Row Level Security (RLS) - 可选
-- 如果需要多用户隔离，可以启用 RLS
-- ALTER TABLE video_generations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

-- 创建策略示例（用户只能访问自己的数据）
-- CREATE POLICY "Users can view own video_generations" ON video_generations
--     FOR SELECT USING (auth.uid() = user_id);
-- 
-- CREATE POLICY "Users can insert own video_generations" ON video_generations
--     FOR INSERT WITH CHECK (auth.uid() = user_id);
-- 
-- CREATE POLICY "Users can update own video_generations" ON video_generations
--     FOR UPDATE USING (auth.uid() = user_id);
-- 
-- CREATE POLICY "Users can delete own video_generations" ON video_generations
--     FOR DELETE USING (auth.uid() = user_id);

