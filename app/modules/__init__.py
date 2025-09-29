"""模块加载器系统

此模块提供一个统一的机制来加载和注册应用中的所有功能模块。
每个功能模块都应该遵循特定的结构，以便能够被自动发现和注册。
"""
import importlib
import os
from flask import Blueprint

# 模块注册表
REGISTERED_MODULES = {}

class ModuleLoader:
    """模块加载器类，负责自动发现和加载功能模块"""
    
    @staticmethod
    def load_module(app, module_name):
        """加载单个模块并注册其蓝图
        
        Args:
            app: Flask应用实例
            module_name: 模块名称
        
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        try:
            # 尝试导入模块的__init__.py
            module = importlib.import_module(f'app.modules.{module_name}')
            
            # 检查模块是否定义了blueprint或bp变量
            if hasattr(module, 'blueprint'):
                blueprint = module.blueprint
                app.register_blueprint(blueprint)
                REGISTERED_MODULES[module_name] = blueprint
                return True
            elif hasattr(module, 'bp'):
                blueprint = module.bp
                app.register_blueprint(blueprint)
                REGISTERED_MODULES[module_name] = blueprint
                return True
            else:
                # 检查模块是否有routes.py文件
                routes_path = os.path.join(os.path.dirname(module.__file__), 'routes.py')
                if os.path.exists(routes_path):
                    routes_module = importlib.import_module(f'app.modules.{module_name}.routes')
                    if hasattr(routes_module, 'bp'):
                        blueprint = routes_module.bp
                        app.register_blueprint(blueprint)
                        REGISTERED_MODULES[module_name] = blueprint
                        return True
                    elif hasattr(routes_module, 'blueprint'):
                        blueprint = routes_module.blueprint
                        app.register_blueprint(blueprint)
                        REGISTERED_MODULES[module_name] = blueprint
                        return True
            
            # 如果没有找到可注册的蓝图，则返回False
            return False
        except ImportError:
            return False
        except Exception:
            return False
            
    @staticmethod
    def load_all_modules(app):
        """自动发现并加载所有功能模块
        
        Args:
            app: Flask应用实例
        
        Returns:
            list: 成功加载的模块名称列表
        """
        loaded_modules = []
        modules_dir = os.path.dirname(__file__)
        
        # 遍历modules目录下的所有子目录
        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            
            # 跳过__pycache__和非目录项
            if item == '__pycache__' or not os.path.isdir(item_path):
                continue
                
            # 跳过没有__init__.py的目录
            if not os.path.exists(os.path.join(item_path, '__init__.py')):
                continue
                
            # 检查模块是否已经注册
            if item in REGISTERED_MODULES:
                loaded_modules.append(item)  # 如果已注册，直接添加到列表
                continue
                
            # 尝试加载模块
            if ModuleLoader.load_module(app, item):
                loaded_modules.append(item)
                
        return loaded_modules

    @staticmethod
    def register_module(app, module_name, blueprint):
        """手动注册一个功能模块
        
        Args:
            app: Flask应用实例
            module_name: 模块名称
            blueprint: Flask蓝图实例
        """
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
            REGISTERED_MODULES[module_name] = blueprint

    @staticmethod
    def get_registered_modules():
        """获取所有已注册的模块
        
        Returns:
            dict: 模块名称到蓝图的映射
        """
        return REGISTERED_MODULES.copy()

# 提供便捷的加载函数
def load_modules(app):
    """加载所有功能模块到Flask应用
    
    Args:
        app: Flask应用实例
        
    Returns:
        list: 成功加载的模块名称列表
    """
    return ModuleLoader.load_all_modules(app)

# 创建默认的模块加载器实例
module_loader = ModuleLoader()