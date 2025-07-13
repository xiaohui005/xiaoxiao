#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查推荐记录
"""

from common.database_manager import DatabaseManager

def check_recommendations():
    """检查推荐记录"""
    try:
        print("检查推荐记录...")
        
        db_manager = DatabaseManager()
        
        # 检查数据库连接
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
        
        # 获取最新推荐记录
        latest_recommendation = db_manager.get_latest_recommendation()
        if latest_recommendation:
            print(f"最新推荐记录: {latest_recommendation}")
        else:
            print("没有找到推荐记录")
        
        # 获取当前期数的推荐
        current_recommendation = db_manager.get_recommendation_by_qishu(latest_qishu)
        if current_recommendation:
            print(f"当前期数推荐: {current_recommendation}")
        else:
            print("当前期数没有推荐记录")
        
        # 如果是0或5尾数，生成新推荐
        if qishu_tail in [0, 5]:
            print(f"期数{latest_qishu}尾数为{qishu_tail}，应该生成新推荐")
            
            # 获取近50期数据
            data = db_manager.get_lottery_data(limit=50)
            print(f"获取到 {len(data)} 条数据")
            
            if not data.empty:
                from common.lottery_analyzer import LotteryAnalyzer
                analyzer = LotteryAnalyzer(data)
                recommendation = analyzer.get_seventh_number_recommendation()
                
                if 'recommendations' in recommendation:
                    recommendations = recommendation['recommendations']
                    if recommendations:
                        recommend_numbers = ','.join([str(rec['number']) for rec in recommendations])
                        success = db_manager.save_recommendation(latest_qishu, recommend_numbers)
                        print(f"保存推荐结果: {'成功' if success else '失败'}")
                        print(f"推荐号码: {recommend_numbers}")
        
        print("✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_recommendations() 