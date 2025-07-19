from flask import Blueprint, render_template, jsonify
from shared_config import get_database_status

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

@main_bp.route('/api/status')
def get_status():
    """获取系统状态API"""
    database_available = get_database_status()
    return jsonify({
        'success': True,
        'database_available': database_available,
        'demo_url': 'http://localhost:5001' if not database_available else None,
        'message': '数据库连接正常' if database_available else '数据库连接不可用，建议使用演示版本'
    })

@main_bp.route('/focus')
def focus():
    """关注点登记页面"""
    return render_template('focus.html')

@main_bp.route('/zodiac')
def zodiac():
    """生肖开奖记录页面"""
    return render_template('zodiac.html') 