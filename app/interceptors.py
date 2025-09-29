import time
import json
import uuid
from flask import request, g
from .database import save_request_log

# 存储请求开始时间
request_start_times = {}

# 定义不需要记录日志的蓝图名称
EXCLUDED_BLUEPRINTS = [
    'base'  # 排除base蓝图下的所有路由
]


def log_request_info():
    """记录请求信息"""
    # 生成请求ID并记录开始时间
    request_id = str(uuid.uuid4())
    request_start_times[request_id] = time.time()
    
    return request_id


def log_response_info(request_id, response):
    """记录响应信息"""
    # 计算处理时间（以毫秒为单位，保留6位小数）
    start_time = request_start_times.pop(request_id, None)
    process_time = round((time.time() - start_time) * 1000, 3) if start_time else None
    # 记录响应信息
    try:
        response_data = json.loads(response.get_data(as_text=True))
    except (ValueError, TypeError):
        response_data = response.get_data(as_text=True)

    # 安全获取JSON数据，避免解析错误
    try:
        request_json = request.get_json(silent=True)
    except Exception as e:
        print(f"解析JSON数据时出错: {e}")
        request_json = None
    
    # 准备存储到数据库的数据
    log_data = {
        'request_id': request_id,
        'method': request.method,
        'url': request.path,
        'client_ip': request.remote_addr,  # 获取客户端IP地址
        'request_headers': dict(request.headers),
        'request_args': dict(request.args),
        'request_form': dict(request.form),
        'request_json': request_json,
        'status_code': response.status_code,
        'response_headers': dict(response.headers),
        'response_data': response_data,
        'process_time': process_time,
        'timestamp': start_time if start_time else time.time(),
        'module': request.blueprint  # 使用蓝图名称作为module
    }
    
    # 保存到数据库
    try:
        save_request_log(log_data)
    except Exception as e:
        print(f"保存请求日志到数据库时出错: {e}")
    
    return response


def request_interceptor(app):
    """注册全局请求拦截器"""
    
    @app.before_request
    def before_request():
        """在每个请求之前记录信息"""
        # 获取当前请求的蓝图名称
        blueprint_name = request.blueprint
        
        # 检查当前蓝图是否在排除列表中
        if blueprint_name in EXCLUDED_BLUEPRINTS:
            return  # 不记录这些蓝图下的请求
        
        request_id = log_request_info()
        # 使用 Flask 的 g 对象存储 request_id，避免并发问题
        g.request_id = request_id

    @app.after_request
    def after_request(response):
        """在每个请求之后记录信息"""
        # 获取当前请求的蓝图名称
        blueprint_name = request.blueprint
        
        # 检查当前蓝图是否在排除列表中
        if blueprint_name in EXCLUDED_BLUEPRINTS:
            return response  # 不记录这些蓝图下的响应
        
        request_id = getattr(g, 'request_id', 'unknown')
        return log_response_info(request_id, response)

    @app.teardown_request
    def teardown_request(exception):
        """请求结束时执行的清理工作"""
        # 获取当前请求的蓝图名称
        blueprint_name = request.blueprint
        
        # 检查当前蓝图是否在排除列表中
        if blueprint_name in EXCLUDED_BLUEPRINTS:
            return  # 不需要清理
        
        if exception:
            print(f"Request failed with exception: {exception}")
        # 清理request_id
        if hasattr(g, 'request_id'):
            delattr(g, 'request_id')