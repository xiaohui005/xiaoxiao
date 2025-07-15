from flask import Blueprint, jsonify, request
from datetime import datetime
import traceback
import pandas as pd
from shared_config import get_database_status, get_db_manager
from common.lottery_analyzer import LotteryAnalyzer

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