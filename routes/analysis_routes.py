from flask import Blueprint, jsonify, request
import traceback
from shared_config import get_database_status, get_db_manager
from common.lottery_analyzer import LotteryAnalyzer

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis')
def get_analysis():
    """获取分析数据API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        print("开始获取分析数据...")
        # 获取所有数据进行分析
        db_manager = get_db_manager()
        data = db_manager.get_all_data_for_analysis()
        
        print(f"分析数据量: {len(data)} 条")
        
        if data.empty:
            return jsonify({'success': True, 'data': {}})
        
        print("开始创建分析器...")
        analyzer = LotteryAnalyzer(data)
        
        print("开始生成分析报告...")
        analysis_result = analyzer.get_summary_report()
        
        print("分析完成")
        return jsonify({
            'success': True,
            'data': analysis_result
        })
    
    except Exception as e:
        print(f"分析API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/trends')
def get_trends():
    """获取趋势分析API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        days = request.args.get('days', 30, type=int)
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=days)
        
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        analyzer = LotteryAnalyzer(data)
        trends_data = analyzer.get_trend_analysis(days=days)
        
        return jsonify({
            'success': True,
            'data': trends_data
        })
    
    except Exception as e:
        print(f"趋势API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/combinations')
def get_combinations():
    """获取组合分析API"""
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
        combinations_data = analyzer.get_combination_analysis()
        
        return jsonify({
            'success': True,
            'data': combinations_data
        })
    
    except Exception as e:
        print(f"组合API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 