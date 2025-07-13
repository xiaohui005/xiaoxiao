from flask import jsonify
from shared_config import get_database_status

def check_database_available():
    """检查数据库是否可用"""
    return get_database_status()

def error_response(message, status_code=500, demo_url=None):
    """生成错误响应"""
    response = {
        'error': message
    }
    if demo_url:
        response['demo_url'] = demo_url
    return jsonify(response), status_code

def success_response(data, message=None):
    """生成成功响应"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response)

def database_unavailable_response():
    """生成数据库不可用的响应"""
    return error_response(
        '数据库连接不可用，请检查配置或使用演示版本',
        503,
        'http://localhost:5001'
    )

def no_data_response():
    """生成无数据响应"""
    return error_response('没有找到数据', 404) 