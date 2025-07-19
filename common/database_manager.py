#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
负责数据库连接和查询操作
"""

import pymysql
import pandas as pd
from datetime import datetime
import traceback
from config.app_config import AppConfig

class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self):
        self.config = AppConfig()
    
    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(
            host=self.config.DATABASE_CONFIG['host'],
            port=self.config.DATABASE_CONFIG['port'],
            user=self.config.DATABASE_CONFIG['user'],
            password=self.config.DATABASE_CONFIG['password'],
            database=self.config.DATABASE_CONFIG['database'],
            charset=self.config.DATABASE_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def get_lottery_data(self, limit=None, start_date=None, end_date=None):
        """获取彩票开奖数据"""
        query = "SELECT * FROM antapp_lotterydraw WHERE draw_time IS NOT NULL"
        conditions = []
        params = []
        
        if start_date:
            conditions.append("draw_time >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("draw_time <= %s")
            params.append(end_date)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY draw_time DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    if results:
                        df = pd.DataFrame(results)
                        print(f"查询到 {len(df)} 条数据")
                        return df
                    else:
                        print("查询到 0 条数据")
                        return pd.DataFrame()
                        
        except Exception as e:
            print(f"数据库查询错误: {e}")
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_statistics(self):
        """获取统计数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 总期数
                    cursor.execute("SELECT COUNT(*) as total FROM antapp_lotterydraw")
                    total_result = cursor.fetchone()
                    total_count = total_result['total'] if total_result else 0
                    
                    # 最新开奖时间
                    cursor.execute("SELECT MAX(draw_time) as latest_time FROM antapp_lotterydraw")
                    latest_result = cursor.fetchone()
                    latest_time = latest_result['latest_time'] if latest_result else None
                    
                    # 最早开奖时间
                    cursor.execute("SELECT MIN(draw_time) as earliest_time FROM antapp_lotterydraw")
                    earliest_result = cursor.fetchone()
                    earliest_time = earliest_result['earliest_time'] if earliest_result else None
                    
                    stats = {
                        'total_count': total_count,
                        'latest_time': latest_time,
                        'earliest_time': earliest_time
                    }
                    
                    print(f"统计数据: {stats}")
                    return stats
                
        except Exception as e:
            print(f"统计查询错误: {e}")
            traceback.print_exc()
            return {
                'total_count': 0,
                'latest_time': None,
                'earliest_time': None,
                'error': str(e)
            }
    
    def get_recent_data(self, limit=10):
        """获取最近开奖数据"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
                    FROM antapp_lotterydraw 
                    WHERE draw_time IS NOT NULL 
                    ORDER BY draw_time DESC 
                    LIMIT %s
                    """
                    cursor.execute(query, (limit,))
                    results = cursor.fetchall()
                    
                    records = []
                    for row in results:
                        record = {
                            'qishu': row['qishu'],
                            'draw_time': row['draw_time'].strftime('%Y-%m-%d %H:%M:%S') if row['draw_time'] else None,
                            'numbers': [
                                row['number1'], row['number2'], row['number3'], 
                                row['number4'], row['number5'], row['number6'], row['number7']
                            ]
                        }
                        records.append(record)
                    
                    print(f"最近数据量: {len(records)} 条")
                    return records
                    
        except Exception as e:
            print(f"最近数据查询错误: {e}")
            traceback.print_exc()
            return []
    
    def get_all_data_for_analysis(self):
        """获取所有数据用于分析"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT * FROM antapp_lotterydraw 
                    WHERE draw_time IS NOT NULL 
                    ORDER BY draw_time DESC
                    """
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        df = pd.DataFrame(results)
                        print(f"分析数据量: {len(df)} 条")
                        return df
                    else:
                        print("分析数据量: 0 条")
                        return pd.DataFrame()
                        
        except Exception as e:
            print(f"分析数据查询错误: {e}")
            traceback.print_exc()
            return pd.DataFrame()
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                conn.close()
            return True
        except Exception as e:
            print(f"数据库连接测试失败: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """执行任意SQL，自动commit，返回select结果或受影响行数"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    # 判断是否是查询
                    if query.strip().lower().startswith('select'):
                        results = cursor.fetchall()
                        return results
                    else:
                        conn.commit()
                        return cursor.rowcount
        except Exception as e:
            print(f"查询执行错误: {e}")
            import traceback; traceback.print_exc()
            return []
    
    def get_latest_qishu(self):
        """获取最新期数"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT MAX(qishu) as latest_qishu FROM antapp_lotterydraw")
                    result = cursor.fetchone()
                    if result and result['latest_qishu'] is not None:
                        return int(result['latest_qishu'])
                    return None
        except Exception as e:
            print(f"获取最新期数错误: {e}")
            return None
    
    def save_recommendation(self, qishu, recommend_numbers, strategy="第七码高频推荐"):
        """保存推荐记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查是否已存在该期数的推荐
                    cursor.execute("SELECT id FROM number8_recommendations WHERE qishu = %s", (qishu,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        cursor.execute("""
                            UPDATE number8_recommendations 
                            SET recommend_numbers = %s, strategy = %s, extra = %s, created_at = CURRENT_TIMESTAMP
                            WHERE qishu = %s
                        """, (recommend_numbers, strategy, "最新系统推荐8码", qishu))
                    else:
                        # 插入新记录
                        cursor.execute("""
                            INSERT INTO number8_recommendations (qishu, recommend_numbers, strategy, extra)
                            VALUES (%s, %s, %s, %s)
                        """, (qishu, recommend_numbers, strategy, "最新系统推荐8码"))
                    
                    conn.commit()
                    print(f"推荐记录已保存: 期数{qishu}, 推荐号码{recommend_numbers}")
                    return True
                    
        except Exception as e:
            print(f"保存推荐记录错误: {e}")
            traceback.print_exc()
            return False
    
    def get_recommendation_by_qishu(self, qishu):
        """根据期数获取推荐记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM number8_recommendations 
                        WHERE qishu = %s 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """, (qishu,))
                    result = cursor.fetchone()
                    return result
        except Exception as e:
            print(f"获取推荐记录错误: {e}")
            return None
    
    def get_latest_recommendation(self):
        """获取最新推荐记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM number8_recommendations 
                        ORDER BY qishu DESC 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    return result
        except Exception as e:
            print(f"获取最新推荐记录错误: {e}")
            return None 

    def add_place(self, name, description):
        """添加关注点"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO places (name, description) VALUES (%s, %s)
                    """, (name, description))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            print(f"添加关注点错误: {e}")
            return None

    def get_places(self):
        """获取所有关注点"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM places ORDER BY created_at DESC")
                    results = cursor.fetchall()
                    # 格式化时间字段
                    for row in results:
                        for field in ('created_at', 'updated_at'):
                            v = row.get(field)
                            if v:
                                if hasattr(v, 'strftime'):
                                    row[field] = v.strftime('%Y-%m-%d')
                                else:
                                    row[field] = str(v)[:10]
                    return results
        except Exception as e:
            print(f"获取关注点错误: {e}")
            return []

    def delete_place(self, place_id):
        """删除关注点"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM places WHERE id = %s", (place_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"删除关注点错误: {e}")
            return False

    def update_place(self, place_id, name=None, description=None, is_correct=None):
        """更新关注点信息"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    fields = []
                    params = []
                    if name is not None:
                        fields.append("name = %s")
                        params.append(name)
                    if description is not None:
                        fields.append("description = %s")
                        params.append(description)
                    if is_correct is not None:
                        fields.append("is_correct = %s")
                        params.append(is_correct)
                    if not fields:
                        return False
                    params.append(place_id)
                    sql = f"UPDATE places SET {', '.join(fields)} WHERE id = %s"
                    cursor.execute(sql, params)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"更新关注点错误: {e}")
            return False

    def get_place_by_id(self, place_id):
        """根据ID获取关注点"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM places WHERE id = %s", (place_id,))
                    result = cursor.fetchone()
                    return result
        except Exception as e:
            print(f"获取关注点详情错误: {e}")
            return None 

    def add_bet(self, place_id, qishu, bet_amount, is_correct=None, win_amount=0.0):
        """添加投注记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO bets (place_id, qishu, bet_amount, is_correct, win_amount)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (place_id, qishu, bet_amount, is_correct, win_amount))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            print(f"添加投注记录错误: {e}")
            return None

    def get_bets(self, place_id=None, qishu=None):
        """获取投注记录列表，可按place_id或qishu筛选"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM bets"
                    conds = []
                    params = []
                    if place_id is not None:
                        conds.append("place_id = %s")
                        params.append(place_id)
                    if qishu is not None:
                        conds.append("qishu = %s")
                        params.append(qishu)
                    if conds:
                        sql += " WHERE " + " AND ".join(conds)
                    sql += " ORDER BY created_at DESC"
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    # 格式化时间字段
                    for row in results:
                        for field in ('created_at', 'updated_at'):
                            v = row.get(field)
                            if v:
                                if hasattr(v, 'strftime'):
                                    row[field] = v.strftime('%Y-%m-%d')
                                else:
                                    row[field] = str(v)[:10]
                    return results
        except Exception as e:
            print(f"获取投注记录错误: {e}")
            return []

    def get_bet_by_id(self, bet_id):
        """根据ID获取投注记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM bets WHERE id = %s", (bet_id,))
                    row = cursor.fetchone()
                    if row:
                        for field in ('created_at', 'updated_at'):
                            v = row.get(field)
                            if v:
                                if hasattr(v, 'strftime'):
                                    row[field] = v.strftime('%Y-%m-%d')
                                else:
                                    row[field] = str(v)[:10]
                    return row
        except Exception as e:
            print(f"获取投注记录详情错误: {e}")
            return None

    def update_bet(self, bet_id, bet_amount=None, is_correct=None, win_amount=None):
        """更新投注记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    fields = []
                    params = []
                    if bet_amount is not None:
                        fields.append("bet_amount = %s")
                        params.append(bet_amount)
                    if is_correct is not None:
                        fields.append("is_correct = %s")
                        params.append(is_correct)
                    if win_amount is not None:
                        fields.append("win_amount = %s")
                        params.append(win_amount)
                    if not fields:
                        print(f'update_bet called but no fields to update! bet_id={bet_id}, bet_amount={bet_amount}, is_correct={is_correct}, win_amount={win_amount}')
                        return False
                    params.append(bet_id)
                    sql = f"UPDATE bets SET {', '.join(fields)} WHERE id = %s"
                    print(f'update_bet SQL: {sql}, params: {params}')  # 新增调试输出
                    cursor.execute(sql, params)
                    conn.commit()
                    # return cursor.rowcount > 0
                    return True
        except Exception as e:
            print(f"更新投注记录错误: {e}")
            return False

    def delete_bet(self, bet_id):
        """删除投注记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM bets WHERE id = %s", (bet_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"删除投注记录错误: {e}")
            return False 

    def add_place_result(self, place_id, qishu, is_correct=None):
        """添加关注点结果记录"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO place_results (place_id, qishu, is_correct)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE is_correct=VALUES(is_correct), updated_at=CURRENT_TIMESTAMP
                    """, (place_id, qishu, is_correct))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            print(f"添加关注点结果错误: {e}")
            return None

    def get_place_results(self, place_id=None, qishu=None, is_correct=None):
        """获取关注点结果列表，可按place_id、qishu、is_correct筛选"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM place_results"
                    conds = []
                    params = []
                    if place_id is not None:
                        conds.append("place_id = %s")
                        params.append(place_id)
                    if qishu is not None:
                        conds.append("qishu = %s")
                        params.append(qishu)
                    if is_correct is not None:
                        conds.append("is_correct = %s")
                        params.append(is_correct)
                    if conds:
                        sql += " WHERE " + " AND ".join(conds)
                    sql += " ORDER BY created_at DESC"
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    for row in results:
                        for field in ('created_at', 'updated_at'):
                            v = row.get(field)
                            if v:
                                if hasattr(v, 'strftime'):
                                    row[field] = v.strftime('%Y-%m-%d')
                                else:
                                    row[field] = str(v)[:10]
                    return results
        except Exception as e:
            print(f"获取关注点结果错误: {e}")
            return []

    def get_place_result_by_id(self, result_id):
        """根据ID获取关注点结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM place_results WHERE id = %s", (result_id,))
                    row = cursor.fetchone()
                    if row:
                        for field in ('created_at', 'updated_at'):
                            v = row.get(field)
                            if v:
                                if hasattr(v, 'strftime'):
                                    row[field] = v.strftime('%Y-%m-%d')
                                else:
                                    row[field] = str(v)[:10]
                    return row
        except Exception as e:
            print(f"获取关注点结果详情错误: {e}")
            return None

    def update_place_result(self, result_id, is_correct=None):
        """更新关注点结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    fields = []
                    params = []
                    if is_correct is not None:
                        fields.append("is_correct = %s")
                        params.append(is_correct)
                    if not fields:
                        return False
                    params.append(result_id)
                    sql = f"UPDATE place_results SET {', '.join(fields)}, updated_at=CURRENT_TIMESTAMP WHERE id = %s"
                    cursor.execute(sql, params)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"更新关注点结果错误: {e}")
            return False

    def delete_place_result(self, result_id):
        """删除关注点结果"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM place_results WHERE id = %s", (result_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"删除关注点结果错误: {e}")
            return False 

    def get_bet_report(self, place_id=None, is_correct=None, start_date=None, end_date=None):
        """投注点报表统计"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT * FROM bets"
                    conds = []
                    params = []
                    if place_id is not None:
                        conds.append("place_id = %s")
                        params.append(place_id)
                    if is_correct is not None:
                        conds.append("is_correct = %s")
                        params.append(is_correct)
                    if start_date is not None:
                        conds.append("created_at >= %s")
                        params.append(start_date)
                    if end_date is not None:
                        conds.append("created_at <= %s")
                        params.append(end_date)
                    if conds:
                        sql += " WHERE " + " AND ".join(conds)
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    total = len(results)
                    total_amount = sum(float(r['bet_amount'] or 0) for r in results)
                    total_win = sum(float(r['win_amount'] or 0) for r in results)
                    correct = sum(1 for r in results if r['is_correct'] == 1)
                    wrong = sum(1 for r in results if r['is_correct'] == 0)
                    unjudged = sum(1 for r in results if r['is_correct'] is None)
                    profit = total_win - total_amount
                    correct_rate = correct / total if total > 0 else 0
                    wrong_rate = wrong / total if total > 0 else 0
                    unjudged_rate = unjudged / total if total > 0 else 0
                    return {
                        'total': total,
                        'total_amount': total_amount,
                        'total_win': total_win,
                        'profit': profit,
                        'correct': correct,
                        'wrong': wrong,
                        'unjudged': unjudged,
                        'correct_rate': correct_rate,
                        'wrong_rate': wrong_rate,
                        'unjudged_rate': unjudged_rate
                    }
        except Exception as e:
            print(f"投注点报表统计错误: {e}")
            traceback.print_exc()
            return None 

    def add_bot_send_queue(self, content):
        """向bot_send_queue表插入一条待发送消息（同一天同内容只插入一次）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查当天是否已有相同内容
                    cursor.execute(
                        """
                        SELECT id FROM bot_send_queue 
                        WHERE content = %s AND DATE(create_time) = CURDATE()
                        """,
                        (content,)
                    )
                    existing = cursor.fetchone()
                    if existing:
                        print(f"今日已存在相同内容，不再插入: {content}")
                        return None
                    cursor.execute(
                        """
                        INSERT INTO bot_send_queue (content, status, send_time, create_time, update_time)
                        VALUES (%s, 0, NULL, NOW(), NOW())
                        """,
                        (content,)
                    )
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            print(f"插入bot_send_queue错误: {e}")
            traceback.print_exc()
            return None 