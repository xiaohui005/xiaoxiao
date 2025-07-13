#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟数据生成器
用于演示版本生成模拟的彩票开奖数据
"""

import random
from datetime import datetime, timedelta

class MockDataGenerator:
    """模拟数据生成器类"""
    
    def __init__(self, number_range=(1, 49)):
        self.min_number = number_range[0]
        self.max_number = number_range[1]
    
    def generate_mock_data(self, count=1000):
        """
        生成模拟的彩票开奖数据
        
        Args:
            count (int): 生成的数据条数
            
        Returns:
            list: 模拟数据列表
        """
        data = []
        base_date = datetime.now()
        
        for i in range(count):
            # 生成期数
            qishu = f"2024{str(i+1).zfill(4)}"
            
            # 生成开奖时间
            draw_time = base_date - timedelta(days=i)
            
            # 生成7个随机号码 (1-49范围)
            numbers = sorted(random.sample(range(self.min_number, self.max_number + 1), 7))
            
            record = {
                'id': i + 1,
                'qishu': qishu,
                'draw_time': draw_time.strftime('%Y-%m-%d %H:%M:%S'),
                'number1': numbers[0],
                'number2': numbers[1],
                'number3': numbers[2],
                'number4': numbers[3],
                'number5': numbers[4],
                'number6': numbers[5],
                'number7': numbers[6],
                'created_at': draw_time.strftime('%Y-%m-%d %H:%M:%S'),
                'remark': f'模拟数据第{i+1}期'
            }
            data.append(record)
        
        return data
    
    def generate_recent_data(self, count=10):
        """
        生成最近的模拟数据
        
        Args:
            count (int): 生成的数据条数
            
        Returns:
            list: 最近数据列表
        """
        all_data = self.generate_mock_data(count * 2)  # 生成更多数据然后取前N条
        recent_data = all_data[:count]
        
        records = []
        for item in recent_data:
            record = {
                'qishu': item['qishu'],
                'draw_time': item['draw_time'],
                'numbers': [
                    item['number1'], item['number2'], item['number3'], 
                    item['number4'], item['number5'], item['number6'], item['number7']
                ]
            }
            records.append(record)
        
        return records
    
    def generate_statistics(self, data_count=1000):
        """
        生成模拟统计数据
        
        Args:
            data_count (int): 数据总数
            
        Returns:
            dict: 统计数据
        """
        base_date = datetime.now()
        earliest_date = base_date - timedelta(days=data_count)
        
        return {
            'total_count': data_count,
            'latest_time': base_date,
            'earliest_time': earliest_date
        } 