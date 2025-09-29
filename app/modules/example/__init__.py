"""示例模块初始化文件

此模块提供示例功能，展示如何按照模块化架构规范实现功能模块。
"""
from .routes import bp

__all__ = ['bp']  # 定义公共API，使外部可以通过from module import *导入bp

# 模块元数据
MODULE_NAME = 'example'
MODULE_VERSION = '1.0.0'
MODULE_DESCRIPTION = '示例功能模块'
MODULE_AUTHOR = '系统管理员'
MODULE_ENABLED = True

# 模块配置示例
MODULE_CONFIG = {
    'debug': False,
    'cache_timeout': 3600,
    'max_items': 100
}

