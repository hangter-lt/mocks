"""示例模块路由定义

此模块提供示例功能，展示如何按照模块化架构规范实现功能模块。
"""
from flask import Blueprint, request, jsonify

# 创建蓝图实例
bp = Blueprint('example', __name__, url_prefix='/example')

@bp.route('/', methods=['GET'])
def get_example():
    """示例API端点 - 获取示例信息
    
    Returns:
        JSON响应: 包含示例信息的JSON对象
    """
    return jsonify({
        'message': '这是一个示例模块',
        'version': '1.0.0',
        'status': 'active'
    })

@bp.route('/data', methods=['GET'])
def get_example_data():
    """示例API端点 - 获取示例数据
    
    Query Parameters:
        count: 返回数据的数量（可选，默认为5）
        type: 数据类型（可选，默认为'default'）
    
    Returns:
        JSON响应: 包含示例数据的JSON对象
    """
    # 获取查询参数
    count = request.args.get('count', default=5, type=int)
    data_type = request.args.get('type', default='default', type=str)
    
    # 生成示例数据
    data = []
    for i in range(count):
        data.append({
            'id': i + 1,
            'value': f'示例数据 {i + 1}',
            'type': data_type
        })
    
    return jsonify({
        'count': len(data),
        'type': data_type,
        'data': data
    })

@bp.route('/submit', methods=['POST'])
def submit_example_data():
    """示例API端点 - 提交示例数据
    
    Request Body:
        JSON对象: 包含要提交的数据
    
    Returns:
        JSON响应: 包含提交结果的JSON对象
    """
    # 获取请求体数据
    if not request.is_json:
        return jsonify({'error': '请求体必须是JSON格式'}), 400
    
    data = request.get_json()
    
    # 简单的数据验证
    if 'name' not in data:
        return jsonify({'error': '缺少必需字段: name'}), 400
    
    # 处理提交的数据
    # 在实际应用中，这里可能会涉及数据库操作、外部API调用等
    
    return jsonify({
        'status': 'success',
        'message': f'已成功提交数据，名称: {data["name"]}',
        'received_data': data
    }), 201