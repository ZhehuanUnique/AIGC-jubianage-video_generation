"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API 配置
API_KEY = os.getenv("API_KEY", "")
SEEDANCE_API_ENDPOINT = os.getenv("SEEDANCE_API_ENDPOINT", "")

# 即梦 AI (火山引擎) AK/SK 配置
# 注意：敏感信息请通过环境变量配置，不要硬编码在代码中
VOLCENGINE_ACCESS_KEY_ID = os.getenv("VOLCENGINE_ACCESS_KEY_ID", "")
VOLCENGINE_SECRET_ACCESS_KEY = os.getenv("VOLCENGINE_SECRET_ACCESS_KEY", "")

# 即梦 API 端点（根据文档调整）
# 即梦 API 使用 visual.volcengineapi.com（cv 服务通过 visual 端点访问）
JIMENG_API_ENDPOINT = os.getenv(
    "JIMENG_API_ENDPOINT",
    "https://visual.volcengineapi.com"
)

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 视频生成默认参数
DEFAULT_VIDEO_SETTINGS = {
    "width": 1024,
    "height": 576,
    "duration": 5,  # 秒
    "fps": 24,
}

# 即梦AI视频生成版本配置
# 设置为 "3.0" 或 "3.0_pro"
# 注意：3.0 Pro 只支持 1080p 首帧，其他情况自动使用 3.0
JIMENG_VIDEO_VERSION = os.getenv("JIMENG_VIDEO_VERSION", "3.0_pro")

# 即梦AI视频生成 req_key 映射
# 3.0 版本的 req_key（根据文档更新）
JIMENG_V30_REQ_KEYS = {
    "720p": {
        "first_frame": "i2v_first_v30_jimeng",
        "first_last_frame": "i2v_first_tail_v30_jimeng"
    },
    "1080p": {
        "first_frame": "i2v_first_v30_1080_jimeng",
        "first_last_frame": "i2v_first_tail_v30_1080_jimeng"
    }
}

# 3.0 Pro 版本的 req_key
# 注意：3.0 Pro 只支持 1080p 首帧功能
JIMENG_V30_PRO_REQ_KEYS = {
    "720p": {
        # 3.0 Pro 不支持 720p，使用 3.0 版本
        "first_frame": "i2v_first_v30_jimeng",
        "first_last_frame": "i2v_first_tail_v30_jimeng"
    },
    "1080p": {
        # 3.0 Pro 只支持首帧，req_key 与 1080P 首帧共用
        "first_frame": "i2v_first_v30_1080_jimeng",
        # 3.0 Pro 不支持首尾帧，使用 3.0 版本
        "first_last_frame": "i2v_first_tail_v30_1080_jimeng"
    }
}

