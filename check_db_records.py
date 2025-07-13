#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的推荐记录
"""

from common.database_manager import DatabaseManager

def check_db_records():
    """检查数据库中的推荐记录"""
    try:
        print("检查数据库中的推荐记录...")
        
        db_manager = DatabaseManager()
        
        # 获取最新期数
        latest_qishu = db_manager.get_latest_qishu()
        print(f"最新期数: {latest_qishu}")
        
        # 获取当前期数的推荐记录
        current_record = db_manager.get_recommendation_by_qishu(latest_qishu)
        if current_record:
            print(f"✅ 当前期数推荐记录:")
            print(f"   ID: {current_record['id']}")
            print(f"   期数: {current_record['qishu']}")
            print(f"   推荐号码: {current_record['recommend_numbers']}")
            print(f"   策略: {current_record['strategy']}")
            print(f"   备注: {current_record['extra']}")
            print(f"   创建时间: {current_record['created_at']}")
        else:
            print("❌ 当前期数没有推荐记录")
        
        # 获取最新推荐记录
        latest_record = db_manager.get_latest_recommendation()
        if latest_record:
            print(f"\n✅ 最新推荐记录:")
            print(f"   ID: {latest_record['id']}")
            print(f"   期数: {latest_record['qishu']}")
            print(f"   推荐号码: {latest_record['recommend_numbers']}")
            print(f"   策略: {latest_record['strategy']}")
            print(f"   备注: {latest_record['extra']}")
            print(f"   创建时间: {latest_record['created_at']}")
        else:
            print("❌ 没有找到推荐记录")
        
        print("\n✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db_records() 