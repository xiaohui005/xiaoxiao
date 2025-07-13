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