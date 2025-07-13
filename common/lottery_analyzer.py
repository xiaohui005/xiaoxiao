#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据分析器
负责数据分析和统计功能
"""

import pandas as pd
import numpy as np
from collections import Counter
import json

class LotteryAnalyzer:
    """彩票数据分析器类"""
    
    def __init__(self, data):
        self.data = data
        self.number_columns = ['number1', 'number2', 'number3', 'number4', 'number5', 'number6', 'number7']
    
    def get_basic_stats(self):
        """获取基础统计信息"""
        if self.data.empty:
            return {}
        
        try:
            # 确保draw_time列是datetime类型
            if 'draw_time' in self.data.columns:
                # 如果draw_time是字符串，转换为datetime
                if self.data['draw_time'].dtype == 'object':
                    self.data['draw_time'] = pd.to_datetime(self.data['draw_time'])
                
                start_date = self.data['draw_time'].min()
                end_date = self.data['draw_time'].max()
                
                stats = {
                    'total_records': len(self.data),
                    'date_range': {
                        'start': start_date.strftime('%Y-%m-%d') if pd.notna(start_date) else None,
                        'end': end_date.strftime('%Y-%m-%d') if pd.notna(end_date) else None
                    },
                    'latest_qishu': self.data['qishu'].iloc[0] if not self.data.empty else None
                }
            else:
                stats = {
                    'total_records': len(self.data),
                    'date_range': {
                        'start': None,
                        'end': None
                    },
                    'latest_qishu': self.data['qishu'].iloc[0] if not self.data.empty else None
                }
            
            return stats
        except Exception as e:
            print(f"基础统计错误: {e}")
            return {
                'total_records': len(self.data),
                'date_range': {'start': None, 'end': None},
                'latest_qishu': None,
                'error': str(e)
            }
    
    def get_number_frequency(self):
        """获取号码出现频率"""
        if self.data.empty:
            return {}
        
        try:
            all_numbers = []
            for col in self.number_columns:
                if col in self.data.columns:
                    all_numbers.extend(self.data[col].tolist())
            
            frequency = Counter(all_numbers)
            sorted_frequency = dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
            
            return {
                'frequency': sorted_frequency,
                'most_common': dict(frequency.most_common(10)),
                'least_common': dict(sorted(frequency.items(), key=lambda x: x[1])[:10])
            }
        except Exception as e:
            print(f"频率分析错误: {e}")
            return {'error': str(e)}
    
    def get_number_analysis(self):
        """获取号码分析"""
        if self.data.empty:
            return {}
        
        try:
            analysis = {}
            
            # 奇偶分析
            odd_even_stats = {}
            for col in self.number_columns:
                if col in self.data.columns:
                    odd_count = len(self.data[self.data[col] % 2 == 1])
                    even_count = len(self.data[self.data[col] % 2 == 0])
                    odd_even_stats[col] = {'odd': odd_count, 'even': even_count}
            
            analysis['odd_even'] = odd_even_stats
            
            # 大小分析 (以50为分界线)
            big_small_stats = {}
            for col in self.number_columns:
                if col in self.data.columns:
                    big_count = len(self.data[self.data[col] > 50])
                    small_count = len(self.data[self.data[col] <= 50])
                    big_small_stats[col] = {'big': big_count, 'small': small_count}
            
            analysis['big_small'] = big_small_stats
            
            # 号码范围分析
            number_ranges = {}
            for col in self.number_columns:
                if col in self.data.columns:
                    ranges = {
                        '1-10': len(self.data[(self.data[col] >= 1) & (self.data[col] <= 10)]),
                        '11-20': len(self.data[(self.data[col] >= 11) & (self.data[col] <= 20)]),
                        '21-30': len(self.data[(self.data[col] >= 21) & (self.data[col] <= 30)]),
                        '31-40': len(self.data[(self.data[col] >= 31) & (self.data[col] <= 40)]),
                        '41-50': len(self.data[(self.data[col] >= 41) & (self.data[col] <= 50)]),
                        '51-60': len(self.data[(self.data[col] >= 51) & (self.data[col] <= 60)]),
                        '61-70': len(self.data[(self.data[col] >= 61) & (self.data[col] <= 70)]),
                        '71-80': len(self.data[(self.data[col] >= 71) & (self.data[col] <= 80)]),
                        '81-90': len(self.data[(self.data[col] >= 81) & (self.data[col] <= 90)]),
                        '91-99': len(self.data[(self.data[col] >= 91) & (self.data[col] <= 99)])
                    }
                    number_ranges[col] = ranges
            
            analysis['number_ranges'] = number_ranges
            
            return analysis
        except Exception as e:
            print(f"号码分析错误: {e}")
            return {'error': str(e)}
    
    def get_trend_analysis(self, days=30):
        """获取趋势分析"""
        if self.data.empty:
            return {}
        
        try:
            # 获取最近N天的数据
            recent_data = self.data.head(days)
            
            trends = {}
            
            # 计算每个号码位置的平均值趋势
            for col in self.number_columns:
                if col in recent_data.columns:
                    trends[col] = {
                        'mean': float(recent_data[col].mean()) if not recent_data[col].empty else 0,
                        'std': float(recent_data[col].std()) if not recent_data[col].empty else 0,
                        'min': float(recent_data[col].min()) if not recent_data[col].empty else 0,
                        'max': float(recent_data[col].max()) if not recent_data[col].empty else 0,
                        'median': float(recent_data[col].median()) if not recent_data[col].empty else 0
                    }
            
            return trends
        except Exception as e:
            print(f"趋势分析错误: {e}")
            return {'error': str(e)}
    
    def get_combination_analysis(self):
        """获取组合分析"""
        if self.data.empty:
            return {}
        
        try:
            # 分析连续号码
            consecutive_count = 0
            for _, row in self.data.iterrows():
                numbers = sorted([row[col] for col in self.number_columns if col in row])
                has_consecutive = False
                for i in range(len(numbers) - 1):
                    if numbers[i+1] - numbers[i] == 1:
                        has_consecutive = True
                        break
                if has_consecutive:
                    consecutive_count += 1
            
            # 分析重复号码
            duplicate_count = 0
            for _, row in self.data.iterrows():
                numbers = [row[col] for col in self.number_columns if col in row]
                if len(set(numbers)) < len(numbers):
                    duplicate_count += 1
            
            return {
                'consecutive_count': consecutive_count,
                'consecutive_percentage': (consecutive_count / len(self.data)) * 100 if len(self.data) > 0 else 0,
                'duplicate_count': duplicate_count,
                'duplicate_percentage': (duplicate_count / len(self.data)) * 100 if len(self.data) > 0 else 0
            }
        except Exception as e:
            print(f"组合分析错误: {e}")
            return {'error': str(e)}
    
    def get_hot_cold_numbers(self):
        """获取冷热号码分析"""
        if self.data.empty:
            return {}
        
        try:
            # 获取最近100期的数据
            recent_data = self.data.head(100)
            
            all_numbers = []
            for col in self.number_columns:
                if col in recent_data.columns:
                    all_numbers.extend(recent_data[col].tolist())
            
            frequency = Counter(all_numbers)
            
            return {
                'hot_numbers': dict(frequency.most_common(10)),
                'cold_numbers': dict(sorted(frequency.items(), key=lambda x: x[1])[:10])
            }
        except Exception as e:
            print(f"冷热号码分析错误: {e}")
            return {'error': str(e)}
    
    def get_summary_report(self):
        """获取综合分析报告"""
        if self.data.empty:
            return {}
        
        try:
            basic_stats = self.get_basic_stats()
            frequency_data = self.get_number_frequency()
            analysis_data = self.get_number_analysis()
            
            return {
                'basic_stats': basic_stats,
                'frequency': frequency_data,
                'analysis': analysis_data
            }
        except Exception as e:
            print(f"综合分析错误: {e}")
            return {'error': str(e)} 