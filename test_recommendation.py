#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试推荐功能
"""

from common.database_manager import DatabaseManager
from common.lottery_analyzer import LotteryAnalyzer

def test_recommendation():
    """测试推荐功能"""
    try:
        print("开始测试推荐功能...")
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        
        # 测试数据库连接
        if not db_manager.test_connection():
            print("❌ 数据库连接失败")
            return
        
        print("✅ 数据库连接成功")
        
        # 获取最新期数
        latest_qishu = db_manager.get_latest_qishu()
        print(f"最新期数: {latest_qishu}")
        
        # 检查期数尾数
        qishu_tail = latest_qishu % 10
        print(f"期数尾数: {qishu_tail}")
        
        # 获取近50期数据
        data = db_manager.get_lottery_data(limit=50)
        print(f"获取到 {len(data)} 条数据")
        
        if data.empty:
            print("❌ 没有获取到数据")
            return
        
        # 创建分析器
        analyzer = LotteryAnalyzer(data)
        
        # 测试第七码推荐
        recommendation = analyzer.get_seventh_number_recommendation()
        print(f"推荐结果: {recommendation}")
        
        # 测试智能推荐
        smart_recommendation = analyzer.get_smart_recommendation(latest_qishu)
        print(f"智能推荐结果: {smart_recommendation}")
        
        # 测试保存推荐
        if 'recommendations' in recommendation:
            recommendations = recommendation['recommendations']
            if recommendations:
                recommend_numbers = ','.join([str(rec['number']) for rec in recommendations])
                success = db_manager.save_recommendation(latest_qishu, recommend_numbers)
                print(f"保存推荐结果: {'成功' if success else '失败'}")
        
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendation() 