from flask import Flask

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)

    # 初始化数据库
    from .database import init_db
    init_db()

    # 注册全局请求拦截器
    from .interceptors import request_interceptor
    request_interceptor(app)

    # 注册base蓝图（原生必要接口）
    from .base.routes import bp as base_bp
    app.register_blueprint(base_bp)

    # 使用模块加载器加载所有功能模块
    from .modules import load_modules
    loaded_modules = load_modules(app)
    print(f"成功加载功能模块: {', '.join(loaded_modules)}")

    # 如果需要手动注册特定模块，可以使用以下方式
    # from .modules import module_loader
    # module_loader.register_module(app, 'module_name', blueprint)

    return app