#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存推荐记录到数据库
"""

from common.database_manager import DatabaseManager
from common.lottery_analyzer import LotteryAnalyzer

def save_current_recommendation():
    """保存当前推荐到数据库"""
    try:
        print("开始生成并保存推荐记录...")
        
        db_manager = DatabaseManager()
        
        # 获取最新期数
        latest_qishu = db_manager.get_latest_qishu()
        if not latest_qishu:
            print("❌ 无法获取最新期数")
            return
        
        print(f"最新期数: {latest_qishu}")
        
        # 获取近50期数据
        data = db_manager.get_lottery_data(limit=50)
        if data.empty:
            print("❌ 没有获取到数据")
            return
        
        print(f"获取到 {len(data)} 条数据")
        
        # 创建分析器并生成推荐
        analyzer = LotteryAnalyzer(data)
        recommendation_data = analyzer.get_seventh_number_recommendation()
        
        if 'error' in recommendation_data:
            print(f"❌ 推荐分析失败: {recommendation_data['error']}")
            return
        
        recommendations = recommendation_data.get('recommendations', [])
        if not recommendations:
            print("❌ 没有生成推荐")
            return
        
        # 格式化推荐号码
        recommend_numbers = ','.join([str(rec['number']) for rec in recommendations])
        print(f"推荐号码: {recommend_numbers}")
        
        # 保存到数据库
        success = db_manager.save_recommendation(latest_qishu, recommend_numbers, "第七码高频推荐")
        
        if success:
            print(f"✅ 推荐记录已保存到数据库")
            print(f"   期数: {latest_qishu}")
            print(f"   推荐号码: {recommend_numbers}")
            print(f"   策略: 第七码高频推荐")
            print(f"   备注: 最新系统推荐8码")
        else:
            print("❌ 保存失败")
        
        # 验证保存结果
        saved_record = db_manager.get_recommendation_by_qishu(latest_qishu)
        if saved_record:
            print(f"✅ 验证成功: 数据库中已存在期数{latest_qishu}的推荐记录")
        else:
            print("❌ 验证失败: 数据库中未找到推荐记录")
        
    except Exception as e:
        print(f"❌ 保存推荐失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    save_current_recommendation() 