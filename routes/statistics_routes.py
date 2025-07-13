from flask import Blueprint, jsonify
import traceback
from shared_config import get_database_status, get_db_manager
from common.lottery_analyzer import LotteryAnalyzer

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/statistics')
def get_statistics():
    """获取统计数据API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        print("开始获取统计数据...")
        db_manager = get_db_manager()
        stats = db_manager.get_statistics()
        print(f"统计数据: {stats}")
        
        # 确保返回的数据格式正确
        if not stats:
            stats = {
                'total_count': 0,
                'latest_time': None,
                'earliest_time': None
            }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        print(f"统计API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/frequency')
def get_frequency():
    """获取号码频率API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=1000)
        
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        analyzer = LotteryAnalyzer(data)
        frequency_data = analyzer.get_number_frequency()
        
        return jsonify({
            'success': True,
            'data': frequency_data
        })
    
    except Exception as e:
        print(f"频率API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/hot-cold')
def get_hot_cold():
    """获取冷热号码API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=1000)
        
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        analyzer = LotteryAnalyzer(data)
        hot_cold_data = analyzer.get_hot_cold_numbers()
        
        return jsonify({
            'success': True,
            'data': hot_cold_data
        })
    
    except Exception as e:
        print(f"冷热号码API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 