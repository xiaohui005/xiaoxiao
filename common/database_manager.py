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