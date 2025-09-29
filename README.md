# Mock API 服务平台

## 项目介绍

Mocks 服务平台是一个轻量级的接口模拟服务，提供可视化的接口mock数据审查功能，并支持通过模块化方式快速增加新的mock接口。该平台采用Flask作为Web框架，实现了自动模块发现和加载机制，便于快速开发和集成新的API模拟功能。

## 产品功能

### 1. 可视化的接口mock数据审查
- 自动记录所有API请求和响应数据
- 支持查看请求头、请求体、响应状态码和响应数据
- 提供请求处理时间统计
- 可按模块分类查看接口调用情况

### 2. 可模块化增加mock接口
- 自动发现和加载功能模块
- 标准化的模块结构设计
- 灵活的路由配置和参数处理
- 支持模块元数据定义

### 3. 其他特性
- 基于Flask的轻量级Web服务
- SQLite数据库存储请求日志
- 全局请求拦截器
- 支持Docker容器化部署

## 架构介绍

### 1. 整体架构

```
mocks/
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化和工厂函数
│   ├── base/               # 基础功能模块
│   ├── database.py         # 数据库操作模块
│   ├── interceptors.py     # 请求拦截器
│   └── modules/            # 功能模块目录
├── run.py                  # 应用启动脚本
├── requirements.txt        # 依赖包列表
└── Dockerfile              # Docker构建文件
```

### 2. 核心组件

#### 应用工厂函数
- 位于 `app/__init__.py`
- 负责创建和配置Flask应用实例
- 初始化数据库、注册拦截器和蓝图
- 调用模块加载器加载所有功能模块

#### 模块加载器
- 位于 `app/modules/__init__.py`
- 提供自动模块发现和加载机制
- 支持手动注册模块
- 维护已注册模块的注册表

#### 数据库模块
- 位于 `app/database.py`
- 提供请求日志存储功能
- 支持查询和管理请求历史

#### 请求拦截器
- 位于 `app/interceptors.py`
- 拦截和记录所有HTTP请求
- 统计请求处理时间

## 使用方式

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. 启动应用

```bash
# 直接启动
python run.py

# 使用gunicorn启动
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### 3. 访问应用

启动后，应用将在 `http://localhost:5000` 上运行,可在web界面查看和分析请求记录

#### 查看模块信息
- 应用启动时会在控制台输出已加载的模块信息
- 包括模块名称、URL前缀和路由数量

#### 访问示例接口
- 示例模块URL: `http://localhost:5000/example`
- 示例数据接口: `http://localhost:5000/example/data`


## 增加模块方法

### 建议使用AI工具新增模块,极大增加效率
1. 将接口文档上传给AI解析
2. 提示词(可以根据需求微调)
```
这是一个接口文档,将该文档中的[接口名称]接口写一份mock代码(使用python的flask框架),请按照以下结构生成文件`__init__.py``routes.py`.`routes.py`要求:创建Blueprint实例并将变量命名为`bp`,Blueprint名称是[模块名称],`__init__.py`要求: 设置`__all__=['bp']`导出变量
```
3. 根据AI输出的结果微调
4. 放入`app/modules/[模块名称]`


### 1. 模块结构规范

要创建一个新的功能模块，请按照以下结构组织文件：

```
app/modules/
└── your_module_name/          # 模块名称目录
    ├── __init__.py            # 模块初始化文件
    └── routes.py              # 路由和接口定义文件
```

### 2. 创建模块文件

#### `__init__.py` 文件示例

```python
"""
[模块名称]模块

此模块提供[模块功能描述]功能。
"""
from .routes import bp

__all__ = ['bp']  # 定义公共API，使外部可以通过from module import *导入bp

# 模块元数据 (非必需)
MODULE_NAME = 'your_module_name'
MODULE_VERSION = '1.0.0'
MODULE_DESCRIPTION = '模块功能描述'
MODULE_AUTHOR = '开发者名称'
MODULE_ENABLED = True

# 模块配置示例 (非必需)
MODULE_CONFIG = {
    # 模块特定配置项
}
```

#### `routes.py` 文件示例

```python
"""
[模块名称]模块路由定义

此文件包含[模块名称]模块的所有API路由和处理函数。
"""
from flask import Blueprint, request, jsonify

# 创建蓝图实例
bp = Blueprint('your_module_name', __name__, url_prefix='/your_module_name')

@bp.route('/', methods=['GET'])
def module_index():
    """模块首页接口
    
    Returns:
        JSON响应: 包含模块信息的JSON对象
    """
    return jsonify({
        'module': 'your_module_name',
        'version': '1.0.0',
        'description': '模块功能描述'
    })
```

### 3. 模块自动加载

创建完模块文件后，应用会在启动时自动发现并加载新模块，无需额外配置。

模块加载器会检查以下条件来决定是否加载模块：
- 模块目录中必须包含 `__init__.py` 文件
- 蓝图变量必须 `bp` 或 `blueprint` 命名
- 模块必须导出蓝图变量 `__all__ = ['bp']`

### 4. 测试新模块

启动应用后，可以通过以下方式验证新模块是否成功加载：
1. 查看应用启动日志中的模块加载信息
2. 访问模块的URL前缀（如 `http://localhost:5000/your_module_name`）
3. 检查请求日志，确认模块接口被正确调用

## Docker部署

项目提供了Docker支持，可以通过以下方式构建和运行Docker容器：

```bash
# 构建Docker镜像
docker build -t mock-api-service .

# 运行Docker容器
docker run -p 5000:5000 mock-api-service

# 使用docker-compose
docker-compose up -d
```

## 注意事项

1. 请确保模块名称不与现有模块冲突
2. 每个模块的URL前缀应唯一，避免路由冲突
3. 生产环境建议使用gunicorn等WSGI服务器代替Flask开发服务器
4. 定期清理请求日志数据库，避免数据过大
5. 如需修改应用配置，请在 `app/__init__.py` 的 `create_app` 函数中进行

## 版本信息

- 版本: 1.0.0
- 开发语言: Python 3.13
- 框架: Flask 3.1.1
- 数据库: SQLite
- 支持部署方式: 原生部署、Docker容器化部署

## TODO

- 增加请求日志清理功能
- 增加动态添加模块,实现仅通过前端配置新模块新接口