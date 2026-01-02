"""
Streamlit 前端界面 - 首帧/首尾帧视频生成
设计参考：即梦 AI 视频生成界面
"""
import streamlit as st
import requests
import time
from typing import Optional
import os
import base64
from io import BytesIO
from PIL import Image

# 页面配置
st.set_page_config(
    page_title="即梦 AI 视频生成",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS - 现代化设计
st.markdown("""
    <style>
    /* 主容器 */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* 首尾帧卡片 */
    .frame-card {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .frame-card:hover {
        border-color: #1f77b4;
        background: #e7f3ff;
    }
    
    .frame-card.has-image {
        border-color: #28a745;
        background: #d4edda;
    }
    
    .frame-icon {
        font-size: 3rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    
    .frame-label {
        font-size: 1.1rem;
        font-weight: 500;
        color: #495057;
        margin-top: 0.5rem;
    }
    
    /* 提示词输入框 */
    .prompt-input {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 1rem;
        font-size: 1rem;
    }
    
    /* 生成按钮 */
    .generate-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .generate-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 参数按钮组 */
    .param-button {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .param-button:hover {
        border-color: #1f77b4;
        background: #f0f7ff;
    }
    
    .param-button.active {
        background: #1f77b4;
        color: white;
        border-color: #1f77b4;
    }
    
    /* 隐藏 Streamlit 默认样式 */
    .stApp {
        background: #ffffff;
    }
    
    /* 标题样式 */
    h1 {
        color: #212529;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# API 配置
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 初始化 session state
if "generated_videos" not in st.session_state:
    st.session_state.generated_videos = []
if "first_frame" not in st.session_state:
    st.session_state.first_frame = None
if "last_frame" not in st.session_state:
    st.session_state.last_frame = None
if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_URL


def generate_video(prompt: str, backend_url: str, 
                   first_frame: Optional[str] = None, 
                   last_frame: Optional[str] = None,
                   duration: int = 5,
                   fps: int = 24) -> dict:
    """调用后端 API 生成视频"""
    url = f"{backend_url}/api/v1/video/generate"
    
    payload = {
        "prompt": prompt,
        "duration": duration,
        "fps": fps,
        "first_frame": first_frame,
        "last_frame": last_frame,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False, 
            "error": str(e), 
            "message": "无法连接到后端服务"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False, 
            "error": str(e), 
            "message": "请求失败"
        }


def check_video_status(task_id: str, backend_url: str) -> dict:
    """查询视频生成状态"""
    url = f"{backend_url}/api/v1/video/status/{task_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": str(e)}


def image_to_base64(image: Image.Image) -> str:
    """将 PIL Image 转换为 base64 字符串"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def main():
    st.title("🎬 即梦 AI 视频生成")
    
    # 侧边栏配置（简化）
    with st.sidebar:
        st.header("⚙️ 配置")
        backend_url = st.text_input(
            "后端 API 地址",
            value=st.session_state.backend_url,
            help="后端服务的地址"
        )
        st.session_state.backend_url = backend_url
        
        st.divider()
        st.info("💡 使用说明：\n1. 上传首帧图片（可选）\n2. 上传尾帧图片（可选）\n3. 输入视频描述\n4. 点击生成视频")
    
    # 主内容区域
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📸 首尾帧设置")
        
        # 首尾帧上传区域
        frame_col1, frame_col2 = st.columns(2, gap="medium")
        
        with frame_col1:
            st.markdown('<div class="frame-card">', unsafe_allow_html=True)
            st.markdown('<div class="frame-icon">➕</div>', unsafe_allow_html=True)
            st.markdown('<div class="frame-label">首帧</div>', unsafe_allow_html=True)
            
            first_frame_file = st.file_uploader(
                "上传首帧图片",
                type=["png", "jpg", "jpeg"],
                key="first_frame_uploader",
                label_visibility="collapsed"
            )
            
            if first_frame_file:
                image = Image.open(first_frame_file)
                st.image(image, use_container_width=True)
                # 转换为 base64
                st.session_state.first_frame = image_to_base64(image)
                st.success("✅ 首帧已上传")
            elif st.session_state.first_frame:
                # 显示已上传的图片
                st.image(st.session_state.first_frame, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with frame_col2:
            st.markdown('<div class="frame-card">', unsafe_allow_html=True)
            st.markdown('<div class="frame-icon">➕</div>', unsafe_allow_html=True)
            st.markdown('<div class="frame-label">尾帧</div>', unsafe_allow_html=True)
            
            last_frame_file = st.file_uploader(
                "上传尾帧图片",
                type=["png", "jpg", "jpeg"],
                key="last_frame_uploader",
                label_visibility="collapsed"
            )
            
            if last_frame_file:
                image = Image.open(last_frame_file)
                st.image(image, use_container_width=True)
                # 转换为 base64
                st.session_state.last_frame = image_to_base64(image)
                st.success("✅ 尾帧已上传")
            elif st.session_state.last_frame:
                # 显示已上传的图片
                st.image(st.session_state.last_frame, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # 视频描述输入
        st.subheader("✍️ 视频描述")
        prompt = st.text_area(
            "输入文字，描述你想创作的画面内容、运动方式等",
            placeholder="例如：一个3D形象的小男孩，在公园滑滑板。",
            height=150,
            help="详细描述视频内容，包括场景、动作、风格等"
        )
        
        st.divider()
        
        # 视频参数
        st.subheader("🎛️ 视频参数")
        
        # 时长选择
        duration_options = [5, 10]
        duration = st.radio(
            "视频时长",
            options=duration_options,
            format_func=lambda x: f"{x}秒",
            horizontal=True,
            index=0
        )
        
        # 生成按钮
        generate_button = st.button(
            "🚀 视频生成",
            type="primary",
            use_container_width=True,
            use_container_width=True
        )
        
        # 生成视频
        if generate_button:
            if not prompt:
                st.error("❌ 请输入视频描述！")
            else:
                with st.spinner("正在生成视频，请稍候..."):
                    result = generate_video(
                        prompt=prompt,
                        backend_url=st.session_state.backend_url,
                        first_frame=st.session_state.first_frame,
                        last_frame=st.session_state.last_frame,
                        duration=duration,
                        fps=24
                    )
                    
                    if result.get("success"):
                        task_id = result.get("task_id")
                        st.success(f"✅ {result.get('message')}")
                        st.info(f"任务 ID: {task_id}")
                        
                        # 保存到 session state
                        st.session_state.generated_videos.append({
                            "task_id": task_id,
                            "prompt": prompt,
                            "first_frame": st.session_state.first_frame is not None,
                            "last_frame": st.session_state.last_frame is not None,
                            "timestamp": time.time(),
                            "status": "processing"
                        })
                        
                        # 轮询状态
                        status_placeholder = st.empty()
                        progress_bar = st.progress(0)
                        
                        max_attempts = 120  # 最多轮询 120 次（约 4 分钟）
                        for attempt in range(max_attempts):
                            status_info = check_video_status(task_id, st.session_state.backend_url)
                            status = status_info.get("status", "processing")
                            progress = status_info.get("progress", 0)
                            
                            warning = status_info.get("warning")
                            note = status_info.get("note")
                            
                            progress_bar.progress(progress / 100)
                            status_text = f"状态: {status} ({progress}%) - 已等待 {attempt * 2} 秒"
                            if warning:
                                status_text += f" ⚠️ {warning}"
                            elif note:
                                status_text += f" ℹ️ {note}"
                            status_placeholder.text(status_text)
                            
                            if status == "completed":
                                video_url = status_info.get("video_url")
                                if video_url:
                                    st.success("✅ 视频生成完成！")
                                    st.video(video_url)
                                    st.session_state.generated_videos[-1]["video_url"] = video_url
                                    st.session_state.generated_videos[-1]["status"] = "completed"
                                break
                            elif status == "failed":
                                error_msg = status_info.get("error", "未知错误")
                                st.error(f"❌ 视频生成失败: {error_msg}")
                                break
                            
                            if warning and "并发限制" in warning:
                                time.sleep(5)
                            else:
                                time.sleep(2)
                        
                        if attempt >= max_attempts - 1:
                            st.warning("⏰ 查询超时，请稍后手动刷新状态")
                    else:
                        error_msg = result.get('message', '生成失败')
                        error_detail = result.get('detail', result.get('error', ''))
                        st.error(f"❌ {error_msg}")
                        if error_detail:
                            st.error(f"错误信息: {error_detail}")
    
    with col2:
        st.subheader("📚 生成历史")
        
        if st.session_state.generated_videos:
            for idx, video_info in enumerate(reversed(st.session_state.generated_videos)):
                with st.expander(f"视频 {len(st.session_state.generated_videos) - idx}: {video_info.get('prompt', '')[:50]}..."):
                    st.write(f"**任务 ID:** {video_info.get('task_id')}")
                    st.write(f"**提示词:** {video_info.get('prompt')}")
                    
                    frame_info = []
                    if video_info.get('first_frame'):
                        frame_info.append("首帧")
                    if video_info.get('last_frame'):
                        frame_info.append("尾帧")
                    if frame_info:
                        st.write(f"**帧设置:** {', '.join(frame_info)}")
                    
                    st.caption(f"状态: {video_info.get('status', 'unknown')}")
                    
                    if video_info.get("video_url"):
                        st.video(video_info["video_url"])
        else:
            st.info("暂无生成历史")


if __name__ == "__main__":
    main()


