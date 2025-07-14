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
    """每个号码+1~+20区间命中/遗漏分析API"""
    if not get_database_status():
        return jsonify({'error': '数据库连接不可用'}), 503
    try:
        db_manager = get_db_manager()
        data = db_manager.get_lottery_data(limit=300)  # 可调整期数
        if data.empty:
            return jsonify({'error': '没有找到数据'}), 404
        # 按qishu升序排列，便于下一期分析
        data = data.sort_values('qishu', ascending=True).reset_index(drop=True)
        records = []
        max_miss = [0]*7
        miss_streak = [0]*7
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
                rng = [(num + j - 1) % 49 + 1 for j in range(1, 21)]
                rng_min = rng[0]
                rng_max = rng[-1]
                hit = entry['next_seventh'] in rng
                if hit:
                    miss_streak[idx] = 0
                else:
                    miss_streak[idx] += 1
                    max_miss[idx] = max(max_miss[idx], miss_streak[idx])
                entry['intervals'].append({
                    'number': num,
                    'range': [rng_min, rng_max],
                    'hit': hit,
                    'miss_streak': miss_streak[idx],
                    'max_miss': max_miss[idx]
                })
            records.append(entry)
        # 计算当前遗漏（最大期数那一行的miss_streak）
        current_miss = [0]*7
        if records:
            # 找到qishu最大的那一条记录
            max_record = max(records, key=lambda r: int(r['qishu']))
            last_intervals = max_record['intervals']
            for idx in range(7):
                current_miss[idx] = last_intervals[idx]['miss_streak']
        return jsonify({'success': True, 'data': records, 'max_miss': max_miss, 'current_miss': current_miss})
    except Exception as e:
        print(f"plus20-intervals API错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 