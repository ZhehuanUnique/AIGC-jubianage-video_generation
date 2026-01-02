"""
Vercel Serverless Function 入口
完全简化版本，直接处理所有请求
"""
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime 的标准 handler 类"""
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        path = self.path.split('?')[0]
        
        # 只处理 API 路径
        if not path.startswith('/api/'):
            # 非 API 路径返回 404（应该由静态文件处理）
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'error': 'Not found', 'path': path, 'message': 'This endpoint only handles /api/* requests'}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            return
        
        # API 路径处理
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 健康检查
        if path == '/api/health':
            response = {'status': 'ok', 'message': '后端服务运行正常'}
        elif path == '/api/v1/assets/list':
            response = {'assets': [], 'count': 0}
        elif path == '/api/v1/assets/characters':
            response = {'characters': [], 'count': 0}
        else:
            self.send_response(404)
            response = {'error': 'Not found', 'path': path}
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        path = self.path.split('?')[0]
        
        if path == '/api/v1/video/generate':
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            try:
                data = json.loads(body.decode('utf-8'))
            except:
                data = {}
            
            # 尝试调用 FastAPI
            response_data = None
            status_code = 200
            
            try:
                import sys
                from pathlib import Path
                
                # 添加项目根目录到路径
                project_root = Path(__file__).parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                # 尝试导入 FastAPI
                try:
                    from backend.api import app
                except ImportError as e:
                    response_data = {
                        'success': False,
                        'error': f'Failed to import FastAPI app: {str(e)}',
                        'message': '后端服务配置错误'
                    }
                    status_code = 500
                else:
                    # 尝试使用 TestClient
                    try:
                        from starlette.testclient import TestClient
                    except ImportError as e:
                        response_data = {
                            'success': False,
                            'error': f'Failed to import TestClient: {str(e)}',
                            'message': '缺少 starlette 依赖'
                        }
                        status_code = 500
                    else:
                        # 调用 FastAPI
                        try:
                            client = TestClient(app)
                            fastapi_response = client.post('/api/v1/video/generate', json=data)
                            
                            # 尝试解析 FastAPI 返回的 JSON
                            try:
                                response_data = fastapi_response.json()
                                status_code = fastapi_response.status_code
                            except:
                                # 如果不是 JSON，返回错误
                                response_data = {
                                    'success': False,
                                    'error': 'FastAPI returned non-JSON response',
                                    'message': '后端返回了无效的响应格式',
                                    'response_text': fastapi_response.text[:200] if hasattr(fastapi_response, 'text') else str(fastapi_response.content)[:200]
                                }
                                status_code = 500
                        except Exception as e:
                            import traceback
                            error_traceback = traceback.format_exc()
                            response_data = {
                                'success': False,
                                'error': str(e),
                                'message': '视频生成失败',
                                'traceback': error_traceback[:500]
                            }
                            status_code = 500
                            
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                response_data = {
                    'success': False,
                    'error': str(e),
                    'message': '处理请求时出错',
                    'traceback': error_traceback[:500]
                }
                status_code = 500
            
            # 确保 response_data 不为 None
            if response_data is None:
                response_data = {
                    'success': False,
                    'error': 'Unknown error',
                    'message': '未知错误'
                }
                status_code = 500
            
            # 发送响应
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        else:
            # 404 响应
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'error': 'Not found', 'path': path}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
