"""
视频后处理服务
支持超分辨率和视频插帧
"""
import os
import tempfile
import subprocess
import requests
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """视频后处理服务"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "video_processing"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def enhance_resolution(
        self,
        video_url: str,
        method: str = "real_esrgan",  # "real_esrgan" 或 "waifu2x"
        scale: int = 2  # 放大倍数（2倍 = 1080P -> 4K）
    ) -> Dict[str, Any]:
        """
        提升视频分辨率（超分辨率）
        
        Args:
            video_url: 原始视频URL
            method: 使用的方法 ("real_esrgan" 或 "waifu2x")
            scale: 放大倍数（2 = 2倍，1080P -> 4K）
        
        Returns:
            {
                "success": bool,
                "output_url": str,
                "original_resolution": (width, height),
                "enhanced_resolution": (width, height),
                "method": str,
                "processing_time": float
            }
        """
        import time
        start_time = time.time()
        
        try:
            # 下载视频
            video_path = await self._download_video(video_url)
            
            # 根据方法选择处理工具
            if method == "real_esrgan":
                output_path = await self._real_esrgan_enhance(video_path, scale)
            elif method == "waifu2x":
                output_path = await self._waifu2x_enhance(video_path, scale)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            # 获取原始和增强后的分辨率
            original_res = await self._get_video_resolution(video_path)
            enhanced_res = await self._get_video_resolution(output_path)
            
            # 上传处理后的视频
            output_url = await self._upload_processed_video(output_path)
            
            # 清理临时文件
            self._cleanup_temp_files([video_path, output_path])
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "output_url": output_url,
                "original_resolution": original_res,
                "enhanced_resolution": enhanced_res,
                "method": method,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"超分辨率处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": method
            }
    
    async def enhance_fps(
        self,
        video_url: str,
        target_fps: int = 60,
        method: str = "rife",  # "rife" 或 "film"
        auto_switch: bool = True  # 是否自动检测大运动并切换
    ) -> Dict[str, Any]:
        """
        提升视频帧率（插帧）
        
        Args:
            video_url: 原始视频URL
            target_fps: 目标帧率（如 60）
            method: 使用的方法 ("rife" 或 "film")
            auto_switch: 是否自动检测大运动并切换到 FILM
        
        Returns:
            {
                "success": bool,
                "output_url": str,
                "original_fps": int,
                "enhanced_fps": int,
                "method": str,
                "auto_switched": bool,  # 是否自动切换了方法
                "processing_time": float
            }
        """
        import time
        start_time = time.time()
        auto_switched = False
        
        try:
            # 下载视频
            video_path = await self._download_video(video_url)
            
            # 获取原始帧率
            original_fps = await self._get_video_fps(video_path)
            
            # 如果启用自动切换，检测是否需要使用 FILM
            if auto_switch and method == "rife":
                has_large_motion = await self._detect_large_motion(video_path)
                if has_large_motion:
                    method = "film"
                    auto_switched = True
                    logger.info("检测到大运动/高遮挡，自动切换到 FILM")
            
            # 根据方法选择处理工具
            if method == "rife":
                output_path = await self._rife_interpolate(video_path, target_fps)
            elif method == "film":
                output_path = await self._film_interpolate(video_path, target_fps)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            # 获取处理后的帧率
            enhanced_fps = await self._get_video_fps(output_path)
            
            # 上传处理后的视频
            output_url = await self._upload_processed_video(output_path)
            
            # 清理临时文件
            self._cleanup_temp_files([video_path, output_path])
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "output_url": output_url,
                "original_fps": original_fps,
                "enhanced_fps": enhanced_fps,
                "method": method,
                "auto_switched": auto_switched,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"帧率提升处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": method
            }
    
    # ========== 私有方法 ==========
    
    async def _download_video(self, video_url: str) -> Path:
        """下载视频到临时文件"""
        response = requests.get(video_url, timeout=300)
        response.raise_for_status()
        
        video_path = self.temp_dir / f"input_{os.urandom(8).hex()}.mp4"
        video_path.write_bytes(response.content)
        
        return video_path
    
    async def _upload_processed_video(self, video_path: Path) -> str:
        """上传处理后的视频到对象存储"""
        from backend.storage import get_storage_service
        
        storage_service = get_storage_service()
        if storage_service:
            # 生成文件名
            video_name = f"enhanced_{os.urandom(8).hex()}.mp4"
            # 上传（注意：这里需要同步读取文件）
            with open(video_path, 'rb') as f:
                # 这里需要根据实际的存储服务实现调整
                # 暂时返回本地路径，实际应该上传到云存储
                pass
        
        # 如果没有对象存储，返回临时URL（实际应该上传到云存储）
        # 这里需要根据实际情况实现
        return str(video_path)
    
    async def _get_video_resolution(self, video_path: Path) -> Tuple[int, int]:
        """获取视频分辨率"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(str(video_path))
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                return (video_stream['width'], video_stream['height'])
        except Exception as e:
            logger.warning(f"获取视频分辨率失败: {e}")
        
        return (0, 0)
    
    async def _get_video_fps(self, video_path: Path) -> int:
        """获取视频帧率"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(str(video_path))
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                fps_str = video_stream.get('r_frame_rate', '24/1')
                num, den = map(int, fps_str.split('/'))
                return int(num / den) if den > 0 else 24
        except Exception as e:
            logger.warning(f"获取视频帧率失败: {e}")
        
        return 24
    
    async def _detect_large_motion(self, video_path: Path) -> bool:
        """
        检测视频是否有大运动/高遮挡
        使用光流法或帧差法检测
        
        Returns:
            True 如果有大运动/高遮挡，False 否则
        """
        try:
            import cv2
            import numpy as np
            
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return False
            
            # 读取前几帧进行检测
            frames = []
            for _ in range(10):
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            
            cap.release()
            
            if len(frames) < 2:
                return False
            
            # 计算帧间差异
            total_diff = 0
            for i in range(1, len(frames)):
                diff = cv2.absdiff(frames[i-1], frames[i])
                total_diff += np.mean(diff)
            
            avg_diff = total_diff / (len(frames) - 1)
            
            # 如果平均差异超过阈值，认为有大运动
            threshold = 30  # 可调整
            return avg_diff > threshold
            
        except Exception as e:
            logger.warning(f"大运动检测失败: {e}，默认使用 RIFE")
            return False
    
    async def _real_esrgan_enhance(self, video_path: Path, scale: int) -> Path:
        """使用 Real-ESRGAN 进行超分辨率"""
        try:
            # 检查是否安装了 realesrgan
            import subprocess
            result = subprocess.run(
                ["realesrgan-ncnn-vulkan", "-h"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                raise ImportError("Real-ESRGAN 未安装或不可用")
            
            output_path = self.temp_dir / f"enhanced_{os.urandom(8).hex()}.mp4"
            
            # 使用 Real-ESRGAN 处理视频
            # 注意：Real-ESRGAN 主要用于图片，视频需要逐帧处理
            # 这里需要实现逐帧处理逻辑
            cmd = [
                "realesrgan-ncnn-vulkan",
                "-i", str(video_path),
                "-o", str(output_path),
                "-s", str(scale),
                "-m", "realesrgan-x4plus"  # 模型名称
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            
            if result.returncode != 0:
                raise RuntimeError(f"Real-ESRGAN 处理失败: {result.stderr.decode()}")
            
            return output_path
            
        except ImportError:
            # 如果未安装，使用 Python 包
            try:
                from realesrgan import RealESRGAN
                import torch
                from PIL import Image
                import cv2
                
                # 初始化模型
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                model = RealESRGAN(device, scale=scale)
                model.load_weights(f'weights/RealESRGAN_x{scale}plus.pth')
                
                # 逐帧处理视频
                cap = cv2.VideoCapture(str(video_path))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                output_path = self.temp_dir / f"enhanced_{os.urandom(8).hex()}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(output_path), fourcc, fps, (width * scale, height * scale))
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 转换为 PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # 超分辨率
                    enhanced_img = model.predict(img)
                    
                    # 转换回 OpenCV 格式
                    enhanced_frame = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
                    out.write(enhanced_frame)
                
                cap.release()
                out.release()
                
                return output_path
                
            except ImportError:
                raise ImportError("Real-ESRGAN 未安装。请安装: pip install realesrgan")
    
    async def _waifu2x_enhance(self, video_path: Path, scale: int) -> Path:
        """使用 Waifu2x 进行超分辨率"""
        try:
            # 使用 waifu2x-ncnn-vulkan 命令行工具
            import subprocess
            
            output_path = self.temp_dir / f"enhanced_{os.urandom(8).hex()}.mp4"
            
            # Waifu2x 主要用于图片，视频需要逐帧处理
            # 这里需要实现逐帧处理逻辑
            cmd = [
                "waifu2x-ncnn-vulkan",
                "-i", str(video_path),
                "-o", str(output_path),
                "-s", str(scale),
                "-m", "models-cunet"  # 模型
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=600)
            
            if result.returncode != 0:
                raise RuntimeError(f"Waifu2x 处理失败: {result.stderr.decode()}")
            
            return output_path
            
        except FileNotFoundError:
            # 如果命令行工具不存在，使用 Python 包
            try:
                from waifu2x import Waifu2x
                import cv2
                from PIL import Image
                import numpy as np
                
                # 初始化模型
                waifu2x = Waifu2x()
                
                # 逐帧处理视频
                cap = cv2.VideoCapture(str(video_path))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                output_path = self.temp_dir / f"enhanced_{os.urandom(8).hex()}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(output_path), fourcc, fps, (width * scale, height * scale))
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 转换为 PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # 超分辨率
                    enhanced_img = waifu2x.process(img, scale=scale)
                    
                    # 转换回 OpenCV 格式
                    enhanced_frame = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
                    out.write(enhanced_frame)
                
                cap.release()
                out.release()
                
                return output_path
                
            except ImportError:
                raise ImportError("Waifu2x 未安装。请安装: pip install waifu2x")
    
    async def _rife_interpolate(self, video_path: Path, target_fps: int) -> Path:
        """使用 RIFE 进行视频插帧"""
        try:
            # 使用 RIFE 命令行工具
            import subprocess
            
            output_path = self.temp_dir / f"interpolated_{os.urandom(8).hex()}.mp4"
            
            # 获取原始帧率
            original_fps = await self._get_video_fps(video_path)
            
            # 计算插帧倍数
            multiplier = target_fps / original_fps
            
            cmd = [
                "python", "-m", "RIFE.interpolate_video",
                "-i", str(video_path),
                "-o", str(output_path),
                "-m", "RIFE/train_log",
                "--exp", "1",
                "--rthreshold", "0.02",
                "--rmodel", "1"
            ]
            
            # 如果使用 TensorFlow Lite 加速
            if os.getenv("USE_TFLITE", "false").lower() == "true":
                cmd.extend(["--tflite"])
            
            result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30分钟超时
            
            if result.returncode != 0:
                raise RuntimeError(f"RIFE 插帧失败: {result.stderr.decode()}")
            
            return output_path
            
        except FileNotFoundError:
            # 如果命令行工具不存在，使用 Python 包
            try:
                from RIFE import RIFE
                import cv2
                
                # 初始化 RIFE 模型
                rife = RIFE()
                
                # 处理视频
                output_path = self.temp_dir / f"interpolated_{os.urandom(8).hex()}.mp4"
                
                # RIFE 处理逻辑
                cap = cv2.VideoCapture(str(video_path))
                original_fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(output_path), fourcc, target_fps, (width, height))
                
                prev_frame = None
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if prev_frame is not None:
                        # 使用 RIFE 插帧
                        interpolated = rife.interpolate(prev_frame, frame)
                        out.write(prev_frame)
                        out.write(interpolated)
                    else:
                        out.write(frame)
                    
                    prev_frame = frame
                
                out.write(prev_frame)  # 写入最后一帧
                
                cap.release()
                out.release()
                
                return output_path
                
            except ImportError:
                raise ImportError("RIFE 未安装。请安装: pip install rife")
    
    async def _film_interpolate(self, video_path: Path, target_fps: int) -> Path:
        """使用 FILM 进行视频插帧（适合大运动/高遮挡）"""
        try:
            # 使用 FILM 命令行工具
            import subprocess
            
            output_path = self.temp_dir / f"interpolated_{os.urandom(8).hex()}.mp4"
            
            cmd = [
                "python", "-m", "film.interpolate_video",
                "-i", str(video_path),
                "-o", str(output_path),
                "--fps", str(target_fps)
            ]
            
            # 如果使用 TensorFlow Lite 加速
            if os.getenv("USE_TFLITE", "false").lower() == "true":
                cmd.extend(["--tflite"])
            
            result = subprocess.run(cmd, capture_output=True, timeout=1800)  # 30分钟超时
            
            if result.returncode != 0:
                raise RuntimeError(f"FILM 插帧失败: {result.stderr.decode()}")
            
            return output_path
            
        except FileNotFoundError:
            # 如果命令行工具不存在，使用 Python 包
            try:
                from film import FILM
                import cv2
                
                # 初始化 FILM 模型
                film = FILM()
                
                # 处理视频
                output_path = self.temp_dir / f"interpolated_{os.urandom(8).hex()}.mp4"
                
                cap = cv2.VideoCapture(str(video_path))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(output_path), fourcc, target_fps, (width, height))
                
                prev_frame = None
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if prev_frame is not None:
                        # 使用 FILM 插帧
                        interpolated = film.interpolate(prev_frame, frame)
                        out.write(prev_frame)
                        out.write(interpolated)
                    else:
                        out.write(frame)
                    
                    prev_frame = frame
                
                out.write(prev_frame)  # 写入最后一帧
                
                cap.release()
                out.release()
                
                return output_path
                
            except ImportError:
                raise ImportError("FILM 未安装。请安装: pip install film")
    
    def _cleanup_temp_files(self, file_paths: list):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if file_path and file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")

