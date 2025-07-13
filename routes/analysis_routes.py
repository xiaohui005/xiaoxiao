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
        # 新增：支持target_col参数，默认7
        target_col = request.args.get('target_col', 7, type=int)
        custom_result = analyzer.get_custom_group_analysis(target_col=target_col)
        return jsonify({
            'success': True,
            'data': custom_result
        })
    
    except Exception as e:
        print(f"组合API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/seventh-number-recommendation')
def get_seventh_number_recommendation():
    """获取第七码高频推荐API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        print("开始获取第七码推荐数据...")
        db_manager = get_db_manager()
        
        # 获取最新期数
        latest_qishu = db_manager.get_latest_qishu()
        if not latest_qishu:
            return jsonify({'error': '无法获取最新期数'}), 404
        try:
            latest_qishu = int(latest_qishu)
        except Exception:
            return jsonify({'error': '最新期数格式错误'}), 500
        
        print(f"最新期数: {latest_qishu}")
        
        # 检查当前期数尾数
        qishu_tail = latest_qishu % 10
        
        if qishu_tail in [0, 5]:
            # 如果是0或5尾数，生成新的推荐
            print(f"期数{latest_qishu}尾数为{qishu_tail}，生成新推荐")
            
            # 获取近50期数据
            data = db_manager.get_lottery_data(limit=50)
            
            print(f"第七码分析数据量: {len(data)} 条")
            
            if data.empty:
                return jsonify({'error': '没有找到数据'}), 404
            
            analyzer = LotteryAnalyzer(data)
            recommendation_data = analyzer.get_seventh_number_recommendation()
            
            if 'error' in recommendation_data:
                return jsonify({'error': recommendation_data['error']}), 500
            
            # 保存推荐到数据库
            recommendations = recommendation_data.get('recommendations', [])
            if recommendations:
                recommend_numbers = ','.join([str(rec['number']) for rec in recommendations])
                db_manager.save_recommendation(latest_qishu, recommend_numbers, "第七码高频推荐")
            
            print("第七码推荐分析完成")
            return jsonify({
                'success': True,
                'data': recommendation_data,
                'current_qishu': latest_qishu,
                'strategy': '新生成推荐'
            })
        else:
            # 否则使用最接近的0或5尾数期数的推荐
            print(f"期数{latest_qishu}尾数为{qishu_tail}，使用历史推荐")
            
            # 首先检查当前期数是否有推荐记录
            current_recommendation = db_manager.get_recommendation_by_qishu(latest_qishu)
            if current_recommendation:
                print(f"找到当前期数{latest_qishu}的推荐记录")
                recommend_numbers = current_recommendation['recommend_numbers'].split(',')
                recommendations = []
                for i, number in enumerate(recommend_numbers):
                    recommendations.append({
                        'number': int(number),
                        'frequency': 0,  # 历史推荐不显示频率
                        'avg_interval': 0,
                        'score': 0.8 - i * 0.1  # 按顺序分配分数
                    })
                
                return jsonify({
                    'success': True,
                    'data': {
                        'recommendations': recommendations,
                        'total_analyzed': 50,
                        'unique_numbers': len(recommendations),
                        'analysis_period': '当前期推荐'
                    },
                    'current_qishu': latest_qishu,
                    'reference_qishu': latest_qishu,
                    'strategy': '使用当前期推荐'
                })
            
            # 如果没有当前期数的推荐，查找最接近的0或5尾数期数
            data = db_manager.get_lottery_data(limit=50)
            analyzer = LotteryAnalyzer(data)
            closest_qishu = analyzer._find_closest_recommendation_qishu(latest_qishu)
            
            # 从数据库获取该期数的推荐
            recommendation_record = db_manager.get_recommendation_by_qishu(closest_qishu)
            
            if recommendation_record:
                recommend_numbers = recommendation_record['recommend_numbers'].split(',')
                recommendations = []
                for i, number in enumerate(recommend_numbers):
                    recommendations.append({
                        'number': int(number),
                        'frequency': 0,  # 历史推荐不显示频率
                        'avg_interval': 0,
                        'score': 0.8 - i * 0.1  # 按顺序分配分数
                    })
                
                return jsonify({
                    'success': True,
                    'data': {
                        'recommendations': recommendations,
                        'total_analyzed': 50,
                        'unique_numbers': len(recommendations),
                        'analysis_period': '历史推荐'
                    },
                    'current_qishu': latest_qishu,
                    'reference_qishu': closest_qishu,
                    'strategy': '使用历史推荐'
                })
            else:
                # 如果没有找到历史推荐，生成新的
                print("未找到历史推荐，生成新推荐")
                recommendation_data = analyzer.get_seventh_number_recommendation()
                
                if 'error' in recommendation_data:
                    return jsonify({'error': recommendation_data['error']}), 500
                
                # 保存推荐到数据库
                recommendations = recommendation_data.get('recommendations', [])
                if recommendations:
                    recommend_numbers = ','.join([str(rec['number']) for rec in recommendations])
                    db_manager.save_recommendation(latest_qishu, recommend_numbers, "第七码高频推荐")
                
                return jsonify({
                    'success': True,
                    'data': recommendation_data,
                    'current_qishu': latest_qishu,
                    'strategy': '新生成推荐'
                })
    
    except Exception as e:
        print(f"第七码推荐API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 