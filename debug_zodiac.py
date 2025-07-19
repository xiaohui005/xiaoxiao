#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("开始调试...")

try:
    from common.database_manager import DatabaseManager
    from shared_config import set_database_status, get_database_status
    print("成功导入模块")
except Exception as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

def debug_zodiac_data():
    print("初始化数据库连接...")
    
    try:
        # 直接初始化数据库管理器
        db_manager = DatabaseManager()
        
        # 测试数据库连接
        try:
            test_connection = db_manager.get_connection()
            test_connection.close()
            set_database_status(True, db_manager)
            print("✅ 数据库连接成功")
        except Exception as e:
            set_database_status(False)
            print(f"⚠️ 数据库连接失败: {e}")
            return
        
        print("数据库状态:", get_database_status())
        
        # 直接测试API的查询逻辑
        print("\n=== 直接测试API查询逻辑 ===")
        
        # 模拟API的完整查询逻辑
        year = "2025"
        limit = 100
        zodiac = "all"
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if year != 'all':
            where_conditions.append("qishu LIKE %s")
            params.append(f"{year}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 直接查询
        direct_query = f"""
            SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
            FROM antapp_lotterydraw 
            WHERE {where_clause}
            ORDER BY qishu DESC 
            LIMIT %s
        """
        params.append(limit)
        
        direct_result = db_manager.execute_query(direct_query, params)
        print(f"直接查询结果数量: {len(direct_result)}")
        if direct_result:
            print(f"直接查询第一条: {direct_result[0]['qishu']}")
            print(f"直接查询最后一条: {direct_result[-1]['qishu']}")
        
        # 检查是否有2025199期
        has_199_direct = any(row['qishu'] == '2025199' for row in direct_result)
        print(f"直接查询是否包含2025199期: {has_199_direct}")
        
        # 检查数据库中的期数排序
        print("\n=== 检查数据库期数排序 ===")
        all_qishu = db_manager.execute_query("SELECT qishu FROM antapp_lotterydraw WHERE qishu LIKE '2025%' ORDER BY qishu DESC LIMIT 10")
        print("数据库中期数排序（前10期）:")
        for i, row in enumerate(all_qishu):
            print(f"{i+1}. {row['qishu']}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_zodiac_data() 