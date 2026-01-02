"""
Render 部署服务器
同时处理 API 路由和静态文件服务
"""
import os
import sys
from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# 导入后端 API（这会创建 app 实例）
from jubianai.backend import api

# 使用后端 API 的 app
app = api.app

# 静态文件目录（项目根目录）
static_root = project_root

# 挂载静态资源目录
from fastapi.staticfiles import StaticFiles

if (static_root / "logo").exists():
    app.mount("/logo", StaticFiles(directory=str(static_root / "logo")), name="logo")

if (static_root / "封面").exists():
    app.mount("/封面", StaticFiles(directory=str(static_root / "封面")), name="封面")

# 服务根目录的静态文件
@app.get("/styles.css")
async def get_css():
    css_path = static_root / "styles.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    return {"error": "CSS file not found"}, 404

@app.get("/main.js")
async def get_js():
    js_path = static_root / "main.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    return {"error": "JS file not found"}, 404

@app.get("/index.mp4")
async def get_video():
    video_path = static_root / "index.mp4"
    if video_path.exists():
        return FileResponse(video_path, media_type="video/mp4")
    return {"error": "Video file not found"}, 404

@app.get("/index.webm")
async def get_webm():
    webm_path = static_root / "index.webm"
    if webm_path.exists():
        return FileResponse(webm_path, media_type="video/webm")
    return {"error": "WebM file not found"}, 404

# 覆盖根路径，返回 index.html（后端 API 的根路径返回 JSON）
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = static_root / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    # Railway 和 Render 都会自动设置 PORT 环境变量
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
