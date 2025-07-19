from flask import Blueprint, jsonify, request
from datetime import datetime
import traceback
import pandas as pd
from shared_config import get_database_status, get_db_manager
from common.lottery_analyzer import LotteryAnalyzer
from config.app_config import AppConfig
from config.zodiac_config import get_zodiac_numbers_by_year, get_zodiac_by_number_and_lunar_date
from common.lottery_analyzer import solar_to_lunar

data_bp = Blueprint('data', __name__)

@data_bp.route('/data')
def get_data():
    """获取开奖数据API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        limit = request.args.get('limit', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        print(f"查询参数: limit={limit}, start_date={start_date}, end_date={end_date}")
        
        # 转换日期格式
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=limit, start_date=start_date, end_date=end_date)
        
        print(f"查询结果: {len(data)} 条数据")
        
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        
        # 转换数据格式
        records = []
        for _, row in data.iterrows():
            try:
                record = {
                    'id': int(row['id']) if pd.notna(row['id']) else None,
                    'qishu': str(row['qishu']) if pd.notna(row['qishu']) else None,
                    'draw_time': row['draw_time'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['draw_time']) else None,
                    'numbers': [
                        int(row['number1']) if pd.notna(row['number1']) else 0,
                        int(row['number2']) if pd.notna(row['number2']) else 0,
                        int(row['number3']) if pd.notna(row['number3']) else 0,
                        int(row['number4']) if pd.notna(row['number4']) else 0,
                        int(row['number5']) if pd.notna(row['number5']) else 0,
                        int(row['number6']) if pd.notna(row['number6']) else 0,
                        int(row['number7']) if pd.notna(row['number7']) else 0
                    ],
                    'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['created_at']) else None,
                    'remark': str(row['remark']) if pd.notna(row['remark']) else None
                }
                records.append(record)
            except Exception as e:
                print(f"数据转换错误: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': records,
            'total': len(records)
        })
    
    except Exception as e:
        print(f"API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/recent')
def get_recent_data():
    """获取最近开奖数据API"""
    if not get_database_status():
        return jsonify({
            'error': '数据库连接不可用，请检查配置或使用演示版本',
            'demo_url': 'http://localhost:5001'
        }), 503
    
    try:
        print("开始获取最近数据...")
        db_manager = get_db_manager()
        records = db_manager.get_recent_data(limit=10)
        
        print(f"最近数据量: {len(records)} 条")
        
        return jsonify({
            'success': True,
            'data': records
        })
    
    except Exception as e:
        print(f"最近数据API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/plus20-intervals')
def get_plus20_intervals():
    """每个号码多个区间命中/遗漏分析API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=300)  # 可调整期数
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        # 区间定义
        interval_defs = [
            (1, 20), (5, 24), (10, 29), (15, 34), (20, 39), (25, 44)
        ]
        # 按qishu升序排列，便于下一期分析
        data = data.sort_values('qishu', ascending=True).reset_index(drop=True)
        records = []
        # 对每个号码位、每个区间都维护miss_streak和max_miss
        miss_streak = [[0 for _ in interval_defs] for _ in range(7)]
        max_miss = [[0 for _ in interval_defs] for _ in range(7)]
        n = len(data)
        for i in range(n-1):
            row = data.iloc[i]
            next_row = data.iloc[i+1]
            entry = {
                'qishu': str(row['qishu']),
                'draw_time': row['draw_time'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['draw_time']) else None,
                'numbers': [int(row[f'number{j}']) for j in range(1,8)],
                'next_seventh': int(next_row['number7']) if pd.notna(next_row['number7']) else None,
                'intervals': []
            }
            for idx in range(7):
                num = int(row[f'number{idx+1}'])
                interval_results = []
                for k, (start, end) in enumerate(interval_defs):
                    rng = [(num + j - 1) % 49 + 1 for j in range(start, end+1)]
                    rng_min = rng[0]
                    rng_max = rng[-1]
                    hit = entry['next_seventh'] in rng
                    if hit:
                        miss_streak[idx][k] = 0
                    else:
                        miss_streak[idx][k] += 1
                        max_miss[idx][k] = max(max_miss[idx][k], miss_streak[idx][k])
                    interval_results.append({
                        'range': [rng_min, rng_max],
                        'hit': hit,
                        'miss_streak': miss_streak[idx][k],
                        'max_miss': max_miss[idx][k]
                    })
                entry['intervals'].append({
                    'number': num,
                    'intervals': interval_results
                })
            records.append(entry)
        # 计算当前遗漏（最大期数那一行的miss_streak）
        current_miss = [[0 for _ in interval_defs] for _ in range(7)]
        if records:
            max_record = max(records, key=lambda r: int(r['qishu']))
            last_intervals = max_record['intervals']
            for idx in range(7):
                for k in range(len(interval_defs)):
                    current_miss[idx][k] = last_intervals[idx]['intervals'][k]['miss_streak']
        alert_threshold = getattr(AppConfig, 'PLUS20_ALERT_THRESHOLD', 3)
        for i in range(7):
            for j in range(len(interval_defs)):
                if current_miss[i][j] > max_miss[i][j] - alert_threshold:
                    db_manager.add_bot_send_queue(
                        f"+1~+20区间分析结果 号码{i+1} 区间{interval_defs[j][0]}~{interval_defs[j][1]} 大于最大的遗漏期数")
        return jsonify({'success': True, 'data': records, 'max_miss': max_miss, 'current_miss': current_miss, 'interval_defs': interval_defs})
    except Exception as e:
        print(f"plus20-intervals API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/latest-lottery')
def get_latest_lottery():
    """获取期号最大的最新一期开奖数据API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data()
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        # 找到qishu最大的那一行
        latest_row = data.loc[data['qishu'].astype(int).idxmax()]
        record = {
            'id': int(latest_row['id']) if pd.notna(latest_row['id']) else None,
            'qishu': str(latest_row['qishu']) if pd.notna(latest_row['qishu']) else None,
            'draw_time': latest_row['draw_time'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(latest_row['draw_time']) else None,
            'numbers': [
                int(latest_row['number1']) if pd.notna(latest_row['number1']) else 0,
                int(latest_row['number2']) if pd.notna(latest_row['number2']) else 0,
                int(latest_row['number3']) if pd.notna(latest_row['number3']) else 0,
                int(latest_row['number4']) if pd.notna(latest_row['number4']) else 0,
                int(latest_row['number5']) if pd.notna(latest_row['number5']) else 0,
                int(latest_row['number6']) if pd.notna(latest_row['number6']) else 0,
                int(latest_row['number7']) if pd.notna(latest_row['number7']) else 0
            ],
            'created_at': latest_row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(latest_row['created_at']) else None,
            'remark': str(latest_row['remark']) if pd.notna(latest_row['remark']) else None
        }
        return jsonify({'success': True, 'data': record})
    except Exception as e:
        print(f"最新开奖API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/minus20-intervals')
def get_minus20_intervals():
    """每个号码-1~-20区间命中/遗漏分析API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=300)  # 可调整期数
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        # 区间定义
        interval_defs = [(1, 20), (5, 24), (10, 29), (15, 34), (20, 39), (25, 44)]  # 多个区间
        # 按qishu升序排列，便于下一期分析
        data = data.sort_values('qishu', ascending=True).reset_index(drop=True)
        records = []
        miss_streak = [[0 for _ in interval_defs] for _ in range(7)]
        max_miss = [[0 for _ in interval_defs] for _ in range(7)]
        n = len(data)
        for i in range(n-1):
            row = data.iloc[i]
            next_row = data.iloc[i+1]
            entry = {
                'qishu': str(row['qishu']),
                'draw_time': row['draw_time'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['draw_time']) else None,
                'numbers': [int(row[f'number{j}']) for j in range(1,8)],
                'next_seventh': int(next_row['number7']) if pd.notna(next_row['number7']) else None,
                'intervals': []
            }
            for idx in range(7):
                num = int(row[f'number{idx+1}'])
                interval_results = []
                for k, (start, end) in enumerate(interval_defs):
                    rng = [(num - j + 49 - 1) % 49 + 1 for j in range(start, end+1)]
                    rng_min = rng[0]
                    rng_max = rng[-1]
                    hit = entry['next_seventh'] in rng
                    if hit:
                        miss_streak[idx][k] = 0
                    else:
                        miss_streak[idx][k] += 1
                        max_miss[idx][k] = max(max_miss[idx][k], miss_streak[idx][k])
                    interval_results.append({
                        'range': [rng_min, rng_max],
                        'hit': hit,
                        'miss_streak': miss_streak[idx][k],
                        'max_miss': max_miss[idx][k]
                    })
                entry['intervals'].append({
                    'number': num,
                    'intervals': interval_results
                })
            records.append(entry)
        # 计算当前遗漏（最大期数那一行的miss_streak）
        current_miss = [[0 for _ in interval_defs] for _ in range(7)]
        if records:
            max_record = max(records, key=lambda r: int(r['qishu']))
            last_intervals = max_record['intervals']
            for idx in range(7):
                for k in range(len(interval_defs)):
                    current_miss[idx][k] = last_intervals[idx]['intervals'][k]['miss_streak']
        alert_threshold = getattr(AppConfig, 'MINUS20_ALERT_THRESHOLD', 3)
        for i in range(7):
            for j in range(len(interval_defs)):
                if current_miss[i][j] > max_miss[i][j] - alert_threshold:
                    db_manager.add_bot_send_queue(
                        f"-1~-20区间分析结果 号码{i+1} 区间{interval_defs[j][0]}~{interval_defs[j][1]} 大于最大的遗漏期数")
        return jsonify({'success': True, 'data': records, 'max_miss': max_miss, 'current_miss': current_miss, 'interval_defs': interval_defs})
    except Exception as e:
        print(f"minus20-intervals API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

# 关注点登记API
@data_bp.route('/places', methods=['GET'])
def api_get_places():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        places = db_manager.get_places()
        return jsonify({'success': True, 'data': places})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/places', methods=['POST'])
def api_add_place():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        description = data.get('description', '')
        if not name:
            return jsonify({'error': '关注点名称不能为空'}), 400
        db_manager = get_db_manager()
        place_id = db_manager.add_place(name, description)
        if place_id:
            return jsonify({'success': True, 'id': place_id})
        else:
            return jsonify({'error': '添加失败，名称可能重复'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/places/<int:place_id>', methods=['DELETE'])
def api_delete_place(place_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        ok = db_manager.delete_place(place_id)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/places/<int:place_id>', methods=['PUT'])
def api_update_place(place_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        description = data.get('description')
        is_correct = data.get('is_correct')
        db_manager = get_db_manager()
        ok = db_manager.update_place(place_id, name=name, description=description, is_correct=is_correct)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/places/<int:place_id>', methods=['GET'])
def api_get_place_by_id(place_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        place = db_manager.get_place_by_id(place_id)
        if place:
            return jsonify({'success': True, 'data': place})
        else:
            return jsonify({'error': '未找到该关注点'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/places/simple', methods=['GET'])
def api_get_places_simple():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        places = db_manager.get_places()
        # 只返回id和name
        simple = [{'id': p['id'], 'name': p['name']} for p in places]
        return jsonify({'success': True, 'data': simple})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 投注点API
@data_bp.route('/bets', methods=['GET'])
def api_get_bets():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        place_id = request.args.get('place_id', type=int)
        qishu = request.args.get('qishu')
        db_manager = get_db_manager()
        bets = db_manager.get_bets(place_id=place_id, qishu=qishu)
        return jsonify({'success': True, 'data': bets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/bets', methods=['POST'])
def api_add_bet():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        place_id = data.get('place_id')
        qishu = data.get('qishu')
        bet_amount = data.get('bet_amount', 0.0)
        is_correct = data.get('is_correct')
        win_amount = data.get('win_amount', 0.0)
        if not place_id or not qishu:
            return jsonify({'error': 'place_id和qishu为必填项'}), 400
        db_manager = get_db_manager()
        bet_id = db_manager.add_bet(place_id, qishu, bet_amount, is_correct, win_amount)
        if bet_id:
            return jsonify({'success': True, 'id': bet_id})
        else:
            return jsonify({'error': '添加失败，可能已存在该期投注'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/bets/<int:bet_id>', methods=['GET'])
def api_get_bet_by_id(bet_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        bet = db_manager.get_bet_by_id(bet_id)
        if bet:
            return jsonify({'success': True, 'data': bet})
        else:
            return jsonify({'error': '未找到该投注记录'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/bets/<int:bet_id>', methods=['PUT'])
def api_update_bet(bet_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        bet_amount = data.get('bet_amount')
        is_correct = data.get('is_correct')
        win_amount = data.get('win_amount')
        db_manager = get_db_manager()
        ok = db_manager.update_bet(bet_id, bet_amount=bet_amount, is_correct=is_correct, win_amount=win_amount)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/bets/<int:bet_id>', methods=['DELETE'])
def api_delete_bet(bet_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        ok = db_manager.delete_bet(bet_id)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/place-results', methods=['GET'])
def api_get_place_results():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        place_id = request.args.get('place_id', type=int)
        qishu = request.args.get('qishu')
        is_correct = request.args.get('is_correct', type=int)
        db_manager = get_db_manager()
        results = db_manager.get_place_results(place_id=place_id, qishu=qishu, is_correct=is_correct)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/place-results', methods=['POST'])
def api_add_place_result():
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        place_id = data.get('place_id')
        qishu = data.get('qishu')
        is_correct = data.get('is_correct')
        db_manager = get_db_manager()
        result_id = db_manager.add_place_result(place_id, qishu, is_correct)
        if result_id:
            return jsonify({'success': True, 'id': result_id})
        else:
            return jsonify({'error': '添加失败，可能已存在该期结果'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/place-results/<int:result_id>', methods=['GET'])
def api_get_place_result_by_id(result_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        result = db_manager.get_place_result_by_id(result_id)
        if result:
            return jsonify({'success': True, 'data': result})
        else:
            return jsonify({'error': '未找到该记录'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/place-results/<int:result_id>', methods=['PUT'])
def api_update_place_result(result_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        data = request.get_json(force=True)
        is_correct = data.get('is_correct')
        db_manager = get_db_manager()
        ok = db_manager.update_place_result(result_id, is_correct=is_correct)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_bp.route('/place-results/<int:result_id>', methods=['DELETE'])
def api_delete_place_result(result_id):
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        ok = db_manager.delete_place_result(result_id)
        return jsonify({'success': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/place-analysis', methods=['GET'])
def api_place_analysis():
    """关注点遗漏、连中等综合分析API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        place_id = request.args.get('place_id', type=int)
        if not place_id:
            return jsonify({'error': 'place_id为必填项'}), 400
        db_manager = get_db_manager()
        # 查询所有结果，按qishu升序
        results = db_manager.get_place_results(place_id=place_id)
        results = sorted(results, key=lambda r: r['qishu'])
        total, correct, wrong, unjudged = 0, 0, 0, 0
        miss_spans, streak_spans = [], []
        miss_dist, streak_dist = {}, {}
        current_miss, max_miss, current_streak, max_streak = 0, 0, 0, 0
        recent_results = []
        for r in results:
            if r['is_correct'] == 1:
                correct += 1
                current_streak += 1
                if current_miss > 0:
                    miss_spans.append(current_miss)
                    miss_dist[str(current_miss)] = miss_dist.get(str(current_miss), 0) + 1
                    max_miss = max(max_miss, current_miss)
                    current_miss = 0
            elif r['is_correct'] == 0:
                wrong += 1
                current_miss += 1
                if current_streak > 0:
                    streak_spans.append(current_streak)
                    streak_dist[str(current_streak)] = streak_dist.get(str(current_streak), 0) + 1
                    max_streak = max(max_streak, current_streak)
                    current_streak = 0
            else:
                unjudged += 1
            total += 1
            recent_results.append({'qishu': r['qishu'], 'is_correct': r['is_correct']})
        # 结尾处理
        if current_miss > 0:
            miss_spans.append(current_miss)
            miss_dist[str(current_miss)] = miss_dist.get(str(current_miss), 0) + 1
            max_miss = max(max_miss, current_miss)
        if current_streak > 0:
            streak_spans.append(current_streak)
            streak_dist[str(current_streak)] = streak_dist.get(str(current_streak), 0) + 1
            max_streak = max(max_streak, current_streak)
        hit_rate = correct / (correct + wrong) if (correct + wrong) > 0 else 0
        # 新增：历史最大遗漏、最大连中、当前遗漏、当前连中
        result_data = {
            'place_id': place_id,
            'total': total,
            'correct': correct,
            'wrong': wrong,
            'unjudged': unjudged,
            'hit_rate': hit_rate,
            'current_miss': current_miss,
            'max_miss': max_miss,
            'current_streak': current_streak,
            'max_streak': max_streak,
            'miss_spans': miss_spans,
            'miss_distribution': miss_dist,
            'streak_spans': streak_spans,
            'streak_distribution': streak_dist,
            'recent_results': recent_results[-30:] # 最近30期
        }
        alert_threshold = getattr(AppConfig, 'PLACE_ANALYSIS_ALERT_THRESHOLD', -13)
        # 获取关注点名称
        place_name = ''
        try:
            place = db_manager.get_place_by_id(place_id)
            if place and 'name' in place:
                place_name = place['name']
        except Exception:
            pass
        # 报警逻辑
        if current_miss > max_miss - alert_threshold:
            db_manager.add_bot_send_queue(f"关注点【{place_name}】区间分析结果 当前遗漏大于最大遗漏期数")
        if current_streak > max_streak - alert_threshold:
            db_manager.add_bot_send_queue(f"关注点【{place_name}】区间分析结果 当前连中大于最大连中期数")
        return jsonify({
            'success': True,
            'data': result_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/bet-report', methods=['GET'])
def api_bet_report():
    """投注点报表统计API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        place_id = request.args.get('place_id', type=int)
        is_correct = request.args.get('is_correct', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        db_manager = get_db_manager()
        data = db_manager.get_bet_report(place_id=place_id, is_correct=is_correct, start_date=start_date, end_date=end_date)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        print(f"bet-report API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/years', methods=['GET'])
def api_get_years():
    """获取数据库中的年份列表API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        
        query = """
            SELECT DISTINCT YEAR(draw_time) as year
            FROM antapp_lotterydraw 
            WHERE draw_time IS NOT NULL
            ORDER BY year DESC
        """
        
        results = db_manager.execute_query(query)
        
        years = []
        for row in results:
            year = row['year']
            if year is not None:
                # 确保年份是有效的
                if isinstance(year, int) and 1900 <= year <= 2100:
                    years.append(str(year))
                elif isinstance(year, str) and year.isdigit() and 1900 <= int(year) <= 2100:
                    years.append(year)
        
        return jsonify({'success': True, 'data': years})
    except Exception as e:
        print(f"years API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/test-2025', methods=['GET'])
def test_2025():
    """测试2025年数据查询"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        
        # 直接查询2025年的最新10期
        query = """
            SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
            FROM antapp_lotterydraw 
            WHERE qishu LIKE '2025%'
            ORDER BY qishu DESC 
            LIMIT 10
        """
        
        results = db_manager.execute_query(query)
        
        # 格式化数据
        formatted_data = []
        for row in results:
            numbers = [row['number1'], row['number2'], row['number3'], row['number4'], row['number5'], row['number6'], row['number7']]
            formatted_data.append({
                'qishu': row['qishu'],
                'draw_time': row['draw_time'],
                'numbers': numbers
            })
        
        return jsonify({
            'success': True, 
            'data': formatted_data,
            'total': len(formatted_data),
            'first_qishu': formatted_data[0]['qishu'] if formatted_data else None
        })
    except Exception as e:
        print(f"test-2025 API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/zodiac-records', methods=['GET'])
def api_get_zodiac_records():
    """生肖开奖记录API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        year = request.args.get('year', 'all')
        limit = request.args.get('limit', 200, type=int)  # 增加默认限制到200
        zodiac = request.args.get('zodiac', 'all')
        
        db_manager = get_db_manager()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if year != 'all':
            where_conditions.append("qishu LIKE %s")
            params.append(f"{year}%")
        
        # 生肖筛选逻辑 - 根据年份获取对应的生肖号码
        
        zodiac_numbers = {}
        if year != 'all' and year.isdigit():
            year_int = int(year)
            for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']:
                numbers = get_zodiac_numbers_by_year(year_int, zodiac)
                if numbers:
                    zodiac_numbers[zodiac] = numbers
        else:
            # 默认使用2025年的生肖映射
            zodiac_numbers = {
                '鼠': [6, 18, 30, 42],
                '牛': [5, 17, 29, 41],
                '虎': [4, 16, 28, 40],
                '兔': [3, 15, 27, 39],
                '龙': [2, 14, 26, 38],
                '蛇': [1, 13, 25, 37, 49],
                '马': [12, 24, 36, 48],
                '羊': [11, 23, 35, 47],
                '猴': [10, 22, 34, 46],
                '鸡': [9, 21, 33, 45],
                '狗': [8, 20, 32, 44],
                '猪': [7, 19, 31, 43]
            }
        
        if zodiac != 'all' and zodiac in zodiac_numbers:
            numbers = zodiac_numbers[zodiac]
            placeholders = ','.join(['%s'] * len(numbers))
            where_conditions.append(f"(number1 IN ({placeholders}) OR number2 IN ({placeholders}) OR number3 IN ({placeholders}) OR number4 IN ({placeholders}) OR number5 IN ({placeholders}) OR number6 IN ({placeholders}) OR number7 IN ({placeholders}))")
            params.extend(numbers * 7)  # 每个号码位置都要检查
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 直接查询，使用简化的逻辑
        if year != 'all':
            query = f"""
                SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
                FROM antapp_lotterydraw 
                WHERE qishu LIKE %s
                ORDER BY qishu DESC 
                LIMIT %s
            """
            params = [f"{year}%", limit]
        else:
            query = f"""
                SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
                FROM antapp_lotterydraw 
                ORDER BY qishu DESC 
                LIMIT %s
            """
            params = [limit]
        
        # 添加调试信息
        print(f"DEBUG: 查询条件: {where_clause}")
        print(f"DEBUG: 查询参数: {params}")
        print(f"DEBUG: 完整SQL: {query}")
        
        results = db_manager.execute_query(query, params)
        
        # 添加调试信息
        print(f"DEBUG: 查询结果数量: {len(results)}")
        if results:
            print(f"DEBUG: 第一条期数: {results[0]['qishu']}")
            print(f"DEBUG: 最后一条期数: {results[-1]['qishu']}")
        
        # 检查是否包含2025199期
        has_199 = any(row['qishu'] == '2025199' for row in results)
        print(f"DEBUG: 是否包含2025199期: {has_199}")
        
        # 格式化数据
        formatted_data = []
        for row in results:
            numbers = [row['number1'], row['number2'], row['number3'], row['number4'], row['number5'], row['number6'], row['number7']]
            lunar = solar_to_lunar(str(row['draw_time']))
            lunar_str = ''
            zodiac_year = None
            if lunar:
                lunar_str = f"{lunar['year']}年{'闰' if lunar['is_leap'] else ''}{lunar['month']}月{lunar['day']}日"
                zodiac_year = lunar['year']
            # 每个号码的生肖，强制用农历年查表
            from config.zodiac_config import get_zodiac_by_number_and_year
            zodiacs = [get_zodiac_by_number_and_year(num, zodiac_year) if zodiac_year else '' for num in numbers]
            formatted_data.append({
                'qishu': row['qishu'],
                'draw_time': row['draw_time'],
                'lunar_date': lunar_str,
                'numbers': numbers,
                'zodiacs': zodiacs,
                'lunar_debug': lunar
            })
        
        return jsonify({'success': True, 'data': formatted_data})
    except Exception as e:
        print(f"zodiac-records API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/favorite-numbers', methods=['GET'])
def api_get_favorite_numbers():
    """获取所有关注号码组及统计"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        year = request.args.get('year', 'all')
        position = int(request.args.get('position', 7))  # 1或7
        # 获取所有关注号码组
        favs = db_manager.execute_query("SELECT id, name, numbers FROM favorite_numbers ORDER BY id ASC")
        # 获取开奖记录
        if year == 'all':
            records = db_manager.execute_query(f"SELECT qishu, number1, number2, number3, number4, number5, number6, number7 FROM antapp_lotterydraw ORDER BY qishu DESC")
        else:
            records = db_manager.execute_query(f"SELECT qishu, number1, number2, number3, number4, number5, number6, number7 FROM antapp_lotterydraw WHERE qishu LIKE %s ORDER BY qishu DESC", [f"{year}%"])
        # 统计每组最大连中/最大遗漏和遗漏/连中详情
        result = []
        for fav in favs:
            nums = [int(x) for x in fav['numbers'].split(',') if x.strip()]
            # 最新期号和开奖号码
            latest_qishu = records[0]['qishu'] if records else ''
            latest_draw = ','.join(str(records[0][f'number{i}']) for i in range(1,8)) if records else ''
            max_streak = 0
            max_miss = 0
            current_streak = 0
            current_miss = 0
            temp_streak = 0
            temp_miss = 0
            miss_details = []
            hit_details = []
            miss_start = None
            miss_qishus = []
            miss_draws = []
            hit_start = None
            hit_qishus = []
            hit_draws = []
            for idx, rec in enumerate(records):
                n = rec[f'number{position}']
                qishu = rec['qishu']
                draw_numbers = ','.join(str(rec[f'number{i}']) for i in range(1,8))
                if n in nums:
                    temp_streak += 1
                    max_streak = max(max_streak, temp_streak)
                    if hit_start is None:
                        hit_start = qishu
                    hit_qishus.append(qishu)
                    hit_draws.append(draw_numbers)
                    if temp_miss > 0:
                        miss_details.append({
                            'start_qishu': miss_start,
                            'end_qishu': records[idx-1]['qishu'] if idx > 0 else qishu,
                            'length': temp_miss,
                            'qishus': miss_qishus[:],
                            'draws': miss_draws[:]
                        })
                        temp_miss = 0
                        miss_qishus = []
                        miss_draws = []
                        miss_start = None
                else:
                    temp_miss += 1
                    max_miss = max(max_miss, temp_miss)
                    temp_streak = 0
                    if miss_start is None:
                        miss_start = qishu
                    miss_qishus.append(qishu)
                    miss_draws.append(draw_numbers)
                    if temp_streak > 0:
                        hit_details.append({
                            'start_qishu': hit_start,
                            'end_qishu': records[idx-1]['qishu'] if idx > 0 else qishu,
                            'length': temp_streak,
                            'qishus': hit_qishus[:],
                            'draws': hit_draws[:]
                        })
                        temp_streak = 0
                        hit_qishus = []
                        hit_draws = []
                        hit_start = None
            if temp_miss > 0:
                miss_details.append({
                    'start_qishu': miss_start,
                    'end_qishu': records[-1]['qishu'] if records else '',
                    'length': temp_miss,
                    'qishus': miss_qishus[:],
                    'draws': miss_draws[:]
                })
            if temp_streak > 0:
                hit_details.append({
                    'start_qishu': hit_start,
                    'end_qishu': records[-1]['qishu'] if records else '',
                    'length': temp_streak,
                    'qishus': hit_qishus[:],
                    'draws': hit_draws[:]
                })
            current_streak = 0
            current_miss = 0
            for rec in records:
                n = rec[f'number{position}']
                if n in nums:
                    if current_miss == 0:
                        current_streak += 1
                    else:
                        break
                else:
                    if current_streak == 0:
                        current_miss += 1
                    else:
                        break
            # 先按期数从小到大排序，正向累加遗漏/连中
            records_sorted = sorted(records, key=lambda x: x['qishu'])
            temp_streak = 0
            temp_miss = 0
            max_streak = 0
            max_miss = 0
            all_details = []
            for rec in records_sorted:
                n = rec[f'number{position}']
                qishu = rec['qishu']
                draw_numbers = ','.join(str(x) for x in nums)
                if n in nums:
                    temp_streak += 1
                    temp_miss = 0
                else:
                    temp_miss += 1
                    temp_streak = 0
                max_streak = max(max_streak, temp_streak)
                max_miss = max(max_miss, temp_miss)
                all_details.append({
                    'qishu': qishu,
                    'numbers': ','.join(str(x) for x in nums),
                    'draw': str(n),  # 只显示判断遗漏用的号码
                    'current_miss': temp_miss,
                    'current_streak': temp_streak,
                    'max_miss': max_miss,
                    'max_streak': max_streak
                })
            # all_details 按期数从大到小排序
            all_details.sort(key=lambda x: x['qishu'], reverse=True)
            result.append({
                'id': fav['id'],
                'name': fav['name'],
                'numbers': ','.join(str(x) for x in nums),
                'max_streak': max_streak,
                'max_miss': max_miss,
                'current_streak': current_streak,
                'current_miss': current_miss,
                'all_details': all_details,
                'latest_qishu': latest_qishu,
                'latest_draw': latest_draw
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"favorite-numbers API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/favorite-numbers', methods=['POST'])
def api_add_favorite_number():
    """添加关注号码组（支持多个号码，英文逗号分隔）"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = request.get_json()
        name = data.get('name', '').strip()
        numbers = data.get('numbers', '').strip()
        # 校验号码格式
        if not name or not numbers:
            return jsonify({'error': '参数错误'}), 400
        nums = [x.strip() for x in numbers.split(',') if x.strip()]
        if not nums or not all(x.isdigit() and 1 <= int(x) <= 49 for x in nums):
            return jsonify({'error': '号码格式错误，必须为1-49的数字，用英文逗号隔开'}), 400
        print(f"准备插入: name={name}, numbers={numbers}")
        db_manager.execute_query("INSERT INTO favorite_numbers (name, numbers) VALUES (%s, %s)", [name, ','.join(nums)])
        print("插入已执行")
        return jsonify({'success': True})
    except Exception as e:
        print(f"add favorite-number API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@data_bp.route('/favorite-numbers/<int:fid>', methods=['DELETE'])
def api_delete_favorite_number(fid):
    """删除关注号码组"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        db_manager.execute_query("DELETE FROM favorite_numbers WHERE id=%s", [fid])
        return jsonify({'success': True})
    except Exception as e:
        print(f"delete favorite-number API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/favorite-numbers/add', methods=['POST'])
def api_add_favorite_number_separate():
    """单独添加关注号码组（支持多个号码，英文逗号分隔）"""
    if not get_database_status():
        print("数据库不可用")
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = request.get_json()
        print(f"收到添加请求: {data}")
        name = data.get('name', '').strip()
        numbers = data.get('numbers', '').strip()
        print(f"参数解析: name={name}, numbers={numbers}")
        # 校验号码格式
        if not name or not numbers:
            print("参数错误")
            return jsonify({'error': '参数错误'}), 400
        nums = [x.strip() for x in numbers.split(',') if x.strip()]
        if not nums or not all(x.isdigit() and 1 <= int(x) <= 49 for x in nums):
            print("号码格式错误")
            return jsonify({'error': '号码格式错误，必须为1-49的数字，用英文逗号隔开'}), 400
        print(f"准备插入: name={name}, numbers={','.join(nums)}")
        db_manager.execute_query("INSERT INTO favorite_numbers (name, numbers) VALUES (%s, %s)", [name, ','.join(nums)])
        print("插入已执行")
        return jsonify({'success': True})
    except Exception as e:
        print(f"add favorite-number (separate) API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/favorite-numbers/<int:fid>', methods=['PUT'])
def api_update_favorite_number(fid):
    """编辑关注号码组（支持多个号码，英文逗号分隔）"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = request.get_json()
        numbers = data.get('numbers', '').strip()
        if not numbers:
            return jsonify({'error': '参数错误'}), 400
        nums = [x.strip() for x in numbers.split(',') if x.strip()]
        if not nums or not all(x.isdigit() and 1 <= int(x) <= 49 for x in nums):
            return jsonify({'error': '号码格式错误，必须为1-49的数字，用英文逗号隔开'}), 400
        db_manager.execute_query("UPDATE favorite_numbers SET numbers=%s WHERE id=%s", [','.join(nums), fid])
        return jsonify({'success': True})
    except Exception as e:
        print(f"update favorite-number API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500 

@data_bp.route('/hot4-recommend-stats', methods=['GET'])
def api_hot4_recommend_stats():
    """热门4码推荐统计接口（所有期数都列出，每期用该期及其之前N期动态统计最热4码，出现次数>=2才推荐）"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        n = int(request.args.get('limit', 100))  # 推荐窗口N
        hit_count = int(request.args.get('hit_count', 1))
        num_count = int(request.args.get('num_count', 4))
        positions = request.args.get('positions', '1,2,3,4,5,6,7')
        pos_list = [int(x) for x in positions.split(',') if x.strip().isdigit() and 1 <= int(x) <= 7]
        source_positions = request.args.get('source_positions', '1,2,3,4,5,6,7')
        source_pos_list = [int(x) for x in source_positions.split(',') if x.strip().isdigit() and 1 <= int(x) <= 7]
        # 获取所有开奖记录（最新在前）
        records = db_manager.execute_query(
            "SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7 FROM antapp_lotterydraw ORDER BY qishu DESC",
            []
        )
        total = len(records)
        from collections import Counter
        result = []
        # records倒序，最新在前，遍历所有可用期数
        for i in range(total-1, 0, -1):  # i=最早到1（最新前一期）
            # 推荐4码用i到i+N-1期（包含本期），窗口不足N期时用能取到的所有前期
            period_records = records[i:min(i+n, total)]
            all_numbers = []
            for rec in period_records:
                for j in source_pos_list:
                    all_numbers.append(rec[f'number{j}'])
            freq = Counter(all_numbers)
            hot_candidates = [(num, cnt) for num, cnt in freq.items() if cnt >= 2]
            hot_candidates.sort(key=lambda x: -x[1])
            hot4 = [num for num, cnt in hot_candidates[:num_count]]
            rec = records[i]
            next_rec = records[i-1]
            recommend = hot4[:]
            next_numbers = [next_rec[f'number{j}'] for j in pos_list]
            hit = [n in recommend for n in next_numbers]
            # 命中位数判断
            overall_hit = sum(hit) >= hit_count
            result.append({
                'qishu': rec['qishu'],
                'draw_time': rec['draw_time'],
                'recommend': recommend,
                'next_qishu': next_rec['qishu'],
                'next_numbers': next_numbers,
                'hit': hit,
                'overall_hit': overall_hit
            })
        # 统计每个位的命中/遗漏、连中/连挂、最大连中/连挂
        pos_stats = []
        for idx, pos in enumerate(pos_list):
            seq = [row['hit'][idx] for row in result]
            max_hit = max_miss = cur_hit = cur_miss = 0
            tmp_hit = tmp_miss = 0
            for h in seq:
                if h:
                    tmp_hit += 1
                    max_hit = max(max_hit, tmp_hit)
                    tmp_miss = 0
                else:
                    tmp_miss += 1
                    max_miss = max(max_miss, tmp_miss)
                    tmp_hit = 0
            for h in reversed(seq):
                if h: cur_hit += 1
                else: break
            for h in reversed(seq):
                if not h: cur_miss += 1
                else: break
            pos_stats.append({
                'pos': pos,
                'max_hit': max_hit,
                'max_miss': max_miss,
                'cur_hit': cur_hit,
                'cur_miss': cur_miss,
                'total_hit': sum(seq),
                'total_miss': len(seq)-sum(seq)
            })
        # 统计整体命中
        overall_seq = [row['overall_hit'] for row in result]
        overall_max_hit = overall_max_miss = overall_cur_hit = overall_cur_miss = 0
        tmp_hit = tmp_miss = 0
        for h in overall_seq:
            if h:
                tmp_hit += 1
                overall_max_hit = max(overall_max_hit, tmp_hit)
                tmp_miss = 0
            else:
                tmp_miss += 1
                overall_max_miss = max(overall_max_miss, tmp_miss)
                tmp_hit = 0
        for h in reversed(overall_seq):
            if h: overall_cur_hit += 1
            else: break
        for h in reversed(overall_seq):
            if not h: overall_cur_miss += 1
            else: break
        overall_stats = {
            'total_hit': sum(overall_seq),
            'total_miss': len(overall_seq)-sum(overall_seq),
            'cur_hit': overall_cur_hit,
            'cur_miss': overall_cur_miss,
            'max_hit': overall_max_hit,
            'max_miss': overall_max_miss
        }
        # 未来预算推荐
        future_period_records = records[0:n]
        all_numbers = []
        for rec in future_period_records:
            for j in source_pos_list:
                all_numbers.append(rec[f'number{j}'])
        freq = Counter(all_numbers)
        hot_candidates = [(num, cnt) for num, cnt in freq.items() if cnt >= 2]
        hot_candidates.sort(key=lambda x: -x[1])
        future_recommend = [num for num, cnt in hot_candidates[:num_count]]
        return jsonify({'success': True, 'result': result, 'pos_stats': pos_stats, 'future_recommend': future_recommend, 'overall_stats': overall_stats})
    except Exception as e:
        print(f"hot4-recommend-stats API错误: {str(e)}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500 