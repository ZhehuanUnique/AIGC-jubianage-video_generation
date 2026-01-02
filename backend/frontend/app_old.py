"""
Streamlit 前端界面
视频生成 Playground
"""
import streamlit as st
import requests
import time
from typing import Optional
import os

# 页面配置
st.set_page_config(
    page_title="视频生成 Playground",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# API 配置（可以通过环境变量或侧边栏配置）
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 初始化 session state
if "generated_videos" not in st.session_state:
    st.session_state.generated_videos = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_URL


def generate_video(prompt: str, width: int, height: int, duration: int, 
                   fps: int, seed: Optional[int], negative_prompt: Optional[str],
                   api_key: str, backend_url: str, 
                   first_frame: Optional[str] = None, last_frame: Optional[str] = None) -> dict:
    """调用后端 API 生成视频"""
    url = f"{backend_url}/api/v1/video/generate"
    
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "duration": duration,
        "fps": fps,
        "seed": seed,
        "negative_prompt": negative_prompt,
        "api_key": api_key if api_key else None,
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
            "message": "无法连接到后端服务",
            "detail": "请检查: 1.后端服务是否运行 2. API 地址是否正确 3.网络连接是否正常"
        }
    except requests.exceptions.Timeout as e:
        return {
            "success": False, 
            "error": str(e), 
            "message": "请求超时",
            "detail": "后端服务响应时间过长，请稍后重试"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False, 
            "error": str(e), 
            "message": "请求失败",
            "detail": f"错误信息: {str(e)} 请检查: 1.后端服务是否运行 2. API 地址是否正确 3.网络连接是否正常"
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


def main():
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["🎬 视频生成", "📦 资产管理", "📚 知识库"])
    
    with tab1:
        video_generation_page()
    
    with tab2:
        assets_management_page()
    
    with tab3:
        knowledge_base_page()


def video_generation_page():
    """视频生成页面"""
    # 标题
    st.markdown('<p class="main-header">🎬 视频生成 Playground</p>', unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # API Key 输入
        api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            help="输入您的 API Key"
        )
        st.session_state.api_key = api_key
        
        # 后端 URL 配置
        backend_url = st.text_input(
            "后端 API 地址",
            value=st.session_state.backend_url,
            help="后端 API 服务的地址"
        )
        st.session_state.backend_url = backend_url
        
        st.divider()
        
        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. 输入视频描述（提示词）
        2. 上传首尾帧图片（可选，用于控制视频起始和结束画面）
        3. 调整视频参数（可选）
        4. 点击"生成视频"按钮
        5. 等待视频生成完成
        """)
        
        st.divider()
        
        st.markdown("### ℹ️ 关于")
        st.markdown("""
        - 模型: 即梦 API
        - 类型: 视频生成
        - 功能: 支持首尾帧控制
        - 后端: FastAPI + 即梦 API
        """)
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 视频生成")
        
        # 提示词输入
        prompt = st.text_area(
            "视频描述（提示词）",
            height=150,
            placeholder="例如：一只可爱的小猫在花园里玩耍，阳光明媚，画面清晰",
            help="详细描述您想要生成的视频内容"
        )
        
        # 负面提示词（可选）
        negative_prompt = st.text_area(
            "负面提示词（可选）",
            height=100,
            placeholder="例如：模糊、低质量、变形",
            help="描述不希望在视频中出现的内容"
        )
        
        # 首尾帧上传
        st.markdown("### 🖼️ 首尾帧（可选）")
        col_first, col_last = st.columns(2)
        
        with col_first:
            first_frame_file = st.file_uploader(
                "首帧图片",
                type=['jpg', 'jpeg', 'png'],
                help="上传视频的第一帧图片，用于控制视频起始画面",
                key="first_frame"
            )
            if first_frame_file:
                # 显示预览
                st.image(first_frame_file, use_container_width=True, caption="首帧预览")
        
        with col_last:
            last_frame_file = st.file_uploader(
                "尾帧图片",
                type=['jpg', 'jpeg', 'png'],
                help="上传视频的最后一帧图片，用于控制视频结束画面",
                key="last_frame"
            )
            if last_frame_file:
                # 显示预览
                st.image(last_frame_file, use_container_width=True, caption="尾帧预览")
        
        # 高级参数
        with st.expander("⚙️ 高级参数", expanded=False):
            col_width, col_height = st.columns(2)
            with col_width:
                width = st.selectbox(
                    "宽度",
                    options=[512, 768, 1024, 1280],
                    index=2,
                    help="视频宽度（像素）"
                )
            with col_height:
                height = st.selectbox(
                    "高度",
                    options=[512, 576, 720, 1024],
                    index=1,
                    help="视频高度（像素）"
                )
            
            col_duration, col_fps = st.columns(2)
            with col_duration:
                duration = st.slider(
                    "时长（秒）",
                    min_value=1,
                    max_value=10,
                    value=5,
                    step=1,
                    help="视频时长"
                )
            with col_fps:
                fps = st.slider(
                    "帧率（FPS）",
                    min_value=12,
                    max_value=30,
                    value=24,
                    step=6,
                    help="视频帧率"
                )
            
            seed = st.number_input(
                "随机种子（可选）",
                min_value=None,
                max_value=None,
                value=None,
                step=1,
                help="用于重现相同结果的种子值，留空则随机生成"
            )
        
        # 生成按钮
        generate_button = st.button("🎬 生成视频", type="primary", use_container_width=True)
        
        # 生成视频
        if generate_button:
            if not prompt:
                st.error("请输入视频描述！")
            elif not api_key:
                st.warning("⚠️ 请在侧边栏输入 API Key")
            else:
                with st.spinner("正在生成视频，请稍候..."):
                    # 处理首尾帧
                    first_frame_data = None
                    last_frame_data = None
                    
                    if first_frame_file:
                        import base64
                        first_frame_file.seek(0)  # 重置文件指针
                        first_frame_data = base64.b64encode(first_frame_file.read()).decode('utf-8')
                    
                    if last_frame_file:
                        import base64
                        last_frame_file.seek(0)  # 重置文件指针
                        last_frame_data = base64.b64encode(last_frame_file.read()).decode('utf-8')
                    
                    result = generate_video(
                        prompt=prompt,
                        width=width,
                        height=height,
                        duration=duration,
                        fps=fps,
                        seed=int(seed) if seed is not None else None,
                        negative_prompt=negative_prompt if negative_prompt else None,
                        api_key=api_key,
                        backend_url=st.session_state.backend_url,
                        first_frame=first_frame_data,
                        last_frame=last_frame_data
                    )
                    
                    if result.get("success"):
                        task_id = result.get("task_id")
                        st.success(f"✅ {result.get('message')}")
                        st.info(f"任务 ID: {task_id}")
                        
                        # 保存到 session state
                        st.session_state.generated_videos.append({
                            "task_id": task_id,
                            "prompt": prompt,
                            "timestamp": time.time(),
                            "status": "processing"
                        })
                        
                        # 轮询状态
                        status_placeholder = st.empty()
                        progress_bar = st.progress(0)
                        
                        max_attempts = 120  # 最多轮询 120 次（约 4 分钟，5秒视频通常需要1-3分钟）
                        for attempt in range(max_attempts):
                            status_info = check_video_status(task_id, st.session_state.backend_url)
                            status = status_info.get("status", "processing")
                            progress = status_info.get("progress", 0)
                            
                            # 显示警告信息（如并发限制）
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
                            
                            # 如果遇到并发限制，增加等待时间
                            if warning and "并发限制" in warning:
                                time.sleep(5)  # 并发限制时等待 5 秒
                            else:
                                time.sleep(2)  # 正常情况每 2 秒查询一次
                        
                        if attempt >= max_attempts - 1:
                            st.warning("⏰ 查询超时，请稍后手动刷新状态")
                        else:
                            st.warning("⏰ 生成时间较长，请稍后刷新页面查看结果")
                    else:
                        error_msg = result.get('message', '生成失败')
                        error_detail = result.get('detail', result.get('error', ''))
                        st.error(f"❌ {error_msg}")
                        if error_detail:
                            st.error(f"错误信息: {error_detail}")
                        # 提供故障排查建议
                        st.info("💡 故障排查：\n1. 检查后端服务是否运行: `ps aux | grep uvicorn`\n2. 检查 API 地址是否正确: " + st.session_state.backend_url + "\n3. 尝试访问健康检查: " + st.session_state.backend_url + "/health")
    
    with col2:
        st.header("📚 历史记录")
        
        if st.session_state.generated_videos:
            for idx, video_info in enumerate(reversed(st.session_state.generated_videos[-10:])):
                with st.container():
                    st.markdown(f"**任务 {idx + 1}**")
                    st.caption(f"提示词: {video_info['prompt'][:50]}...")
                    st.caption(f"状态: {video_info.get('status', 'unknown')}")
                    
                    if video_info.get("video_url"):
                        st.video(video_info["video_url"])
                    
                    st.divider()
        else:
            st.info("暂无历史记录")


def assets_management_page():
    """资产管理页面"""
    st.markdown('<p class="main-header">📦 资产管理</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("上传资产")
        st.markdown("""
        **文件名格式要求：**
        - 格式：`人物名-视图类型.扩展名`
        - 示例：`小明-正视图.jpg`、`小美-侧视图.png`
        - 支持格式：JPG, PNG, GIF, WebP
        """)
        
        uploaded_files = st.file_uploader(
            "选择图片文件",
            type=['jpg', 'jpeg', 'png', 'gif', 'webp'],
            accept_multiple_files=True,
            help="可以一次上传多个文件"
        )
        
        if uploaded_files and st.button("📤 上传资产", type="primary", use_container_width=True):
            upload_assets(uploaded_files)
    
    with col2:
        st.header("资产预览")
        display_assets()


def upload_assets(uploaded_files):
    """上传资产文件"""
    if not uploaded_files:
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    success_count = 0
    error_count = 0
    
    for idx, file in enumerate(uploaded_files):
        try:
            status_text.text(f"正在上传: {file.name} ({idx + 1}/{len(uploaded_files)})")
            
            # 调用后端 API 上传
            url = f"{st.session_state.backend_url}/api/v1/assets/upload"
            files = {"file": (file.name, file.getvalue(), file.type)}
            
            response = requests.post(url, files=files, timeout=30)
            response.raise_for_status()
            
            success_count += 1
        except Exception as e:
            st.error(f"上传失败 {file.name}: {str(e)}")
            error_count += 1
        
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.empty()
    progress_bar.empty()
    
    if success_count > 0:
        st.success(f"✅ 成功上传 {success_count} 个文件")
    if error_count > 0:
        st.warning(f"⚠️ {error_count} 个文件上传失败")
    
    # 刷新页面以显示新上传的资产
    time.sleep(0.5)
    st.rerun()


def display_assets():
    """显示资产，按人物分组"""
    try:
        url = f"{st.session_state.backend_url}/api/v1/assets/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        assets_by_character = response.json()
        
        if not assets_by_character:
            st.info("📭 暂无资产，请先上传")
            return
        
        # 按人物分组显示
        for character_name, assets in assets_by_character.items():
            st.markdown(f"### 👤 {character_name}")
            
            # 显示该人物的所有资产
            cols = st.columns(min(len(assets), 4))  # 每行最多4个
            
            for idx, asset in enumerate(assets):
                col_idx = idx % 4
                with cols[col_idx]:
                    try:
                        # 获取图片URL - 使用存储的文件路径中的文件名
                        stored_filename = Path(asset.get('file_path', '')).name if asset.get('file_path') else asset.get('filename', '')
                        image_url = f"{st.session_state.backend_url}/api/v1/assets/{stored_filename}"
                        
                        # 显示图片
                        st.image(image_url, use_container_width=True, caption=asset.get('view_type', '未知'))
                        
                        # 删除按钮
                        delete_key = f"delete_{character_name}_{idx}_{hash(stored_filename) % 10000}"
                        if st.button("🗑️ 删除", key=delete_key, use_container_width=True):
                            delete_asset_file(stored_filename)
                    except Exception as e:
                        st.error(f"加载失败: {str(e)}")
            
            st.divider()
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 无法连接到后端服务: {str(e)}")
        st.info("请确保后端服务正在运行")


def delete_asset_file(filename: str):
    """删除资产文件"""
    try:
        url = f"{st.session_state.backend_url}/api/v1/assets/{filename}"
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        st.success(f"✅ 已删除: {filename}")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.error(f"删除失败: {str(e)}")


def knowledge_base_page():
    """知识库页面"""
    st.markdown('<p class="main-header">📚 知识库管理</p>', unsafe_allow_html=True)
    
    st.info("""
    **知识库功能说明：**
    
    1. **剧本上传**：上传剧本文件，系统将自动识别其中的人物
    2. **人物一致性**：根据剧本中的人物，自动匹配已上传的资产
    3. **场景一致性**：保持场景的连贯性和上下文关系
    4. **向量化存储**：（可选）将剧本和资产转为向量，用于智能检索
    
    **实现方式：**
    - 使用多模态大模型提取人物和场景特征
    - 使用向量数据库存储和检索
    - 使用 RAG（检索增强生成）技术保持一致性
    
    ⚠️ 此功能正在开发中，后续版本将支持。
    """)
    
    st.header("📄 剧本上传")
    script_file = st.file_uploader(
        "上传剧本文件",
        type=['txt', 'md', 'docx'],
        help="支持 TXT、Markdown、Word 格式"
    )
    
    if script_file and st.button("📤 上传并分析", type="primary"):
        st.warning("⚠️ 剧本分析功能正在开发中，敬请期待！")


if __name__ == "__main__":
    main()

