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
import lunarcalendar
from lunarcalendar.converter import Solar, Lunar
from datetime import datetime

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
    
    def get_seventh_number_recommendation(self):
        """获取第七码高频推荐分析"""
        if self.data.empty:
            return {}
        
        try:
            # 确保数据按时间倒序排列（最新的在前面）
            sorted_data = self.data.sort_values('qishu', ascending=False).reset_index(drop=True)
            
            # 获取第七码数据
            seventh_numbers = sorted_data['number7'].tolist() if 'number7' in sorted_data.columns else []
            
            if not seventh_numbers:
                return {'error': '没有找到第七码数据'}
            
            # 统计每个号码的出现次数
            frequency = Counter(seventh_numbers)
            
            # 计算每个号码的平均间隔
            intervals = {}
            for number in frequency.keys():
                positions = [i for i, num in enumerate(seventh_numbers) if num == number]
                if len(positions) > 1:
                    gaps = [positions[i] - positions[i-1] for i in range(1, len(positions))]
                    avg_interval = sum(gaps) / len(gaps)
                else:
                    avg_interval = len(seventh_numbers)
                intervals[number] = round(avg_interval, 1)
            
            # 计算高频（出现次数前5）、热门（最近10期出现过）、间隔优选（最接近5期的2个）
            freq_sorted = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            high_freq_numbers = set([num for num, _ in freq_sorted[:5]])
            recent_10 = seventh_numbers[:10]
            hot_numbers = set([num for num in set(recent_10)])
            interval_sorted = sorted(intervals.items(), key=lambda x: abs(x[1] - 5))
            best_interval_numbers = set([num for num, _ in interval_sorted[:2]])
            
            # 创建推荐列表，结合频率和间隔
            recommendations = []
            for number, freq in frequency.items():
                avg_interval = intervals.get(number, 0)
                freq_score = freq / max(frequency.values()) if max(frequency.values()) > 0 else 0
                interval_score = 1 - abs(avg_interval - 5) / 10
                interval_score = max(0, min(1, interval_score))
                total_score = freq_score * 0.6 + interval_score * 0.4
                # 推荐原因
                if number in high_freq_numbers:
                    reason = "高频"
                elif number in hot_numbers:
                    reason = "近期热门"
                elif number in best_interval_numbers:
                    reason = "间隔优选"
                else:
                    reason = "综合推荐"
                recommendations.append({
                    'number': number,
                    'frequency': freq,
                    'avg_interval': avg_interval,
                    'score': round(total_score, 3),
                    'reason': reason
                })
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            top_recommendations = recommendations[:8]
            return {
                'recommendations': top_recommendations,
                'total_analyzed': len(seventh_numbers),
                'unique_numbers': len(frequency),
                'analysis_period': '近50期'
            }
        except Exception as e:
            print(f"第七码推荐分析错误: {e}")
            return {'error': str(e)}
    
    def get_smart_recommendation(self, current_qishu):
        """获取智能推荐（根据期数尾数决定策略）"""
        if self.data.empty:
            return {}
        
        try:
            # 检查当前期数尾数
            qishu_tail = current_qishu % 10
            
            # 如果是0或5尾数，生成新的推荐
            if qishu_tail in [0, 5]:
                print(f"期数{current_qishu}尾数为{qishu_tail}，生成新推荐")
                return self.get_seventh_number_recommendation()
            else:
                # 否则使用最接近的0或5尾数期数的推荐
                # 找到最接近的0或5尾数期数
                closest_qishu = self._find_closest_recommendation_qishu(current_qishu)
                print(f"期数{current_qishu}使用期数{closest_qishu}的推荐")
                
                return {
                    'recommendations': [],  # 这里需要从数据库获取
                    'reference_qishu': closest_qishu,
                    'strategy': '使用历史推荐',
                    'message': f'使用期数{closest_qishu}的推荐'
                }
                
        except Exception as e:
            print(f"智能推荐分析错误: {e}")
            return {'error': str(e)}
    
    def _find_closest_recommendation_qishu(self, current_qishu):
        """找到最接近的0或5尾数期数"""
        try:
            # 获取所有期数
            all_qishu = self.data['qishu'].tolist()
            
            # 确保所有期数都是整数
            all_qishu = [int(q) for q in all_qishu if q is not None]
            
            # 找到所有0或5尾数的期数
            recommendation_qishu = [q for q in all_qishu if q % 10 in [0, 5]]
            
            if not recommendation_qishu:
                return current_qishu
            
            # 找到最接近当前期数的推荐期数
            closest_qishu = min(recommendation_qishu, key=lambda x: abs(x - current_qishu))
            return closest_qishu
            
        except Exception as e:
            print(f"查找最接近推荐期数错误: {e}")
            return current_qishu 

    def get_custom_group_analysis(self, target_col=7):
        """
        组合分析：
        - 组1：尾数0,1,2,3,4，去掉11,22,33,44
        - 组2：尾数5,6,7,8，去掉所有9尾
        - 统计目标码（默认第7个码）属于哪组，遗漏和连续命中
        """
        if self.data.empty:
            return {}
        try:
            # 按qishu升序排序
            if 'qishu' in self.data.columns:
                sorted_data = self.data.sort_values('qishu', ascending=True).reset_index(drop=True)
            else:
                sorted_data = self.data.reset_index(drop=True)
            # 生成组1和组2号码集合
            group1 = set()
            group2 = set()
            for n in range(1, 50):
                tail = n % 10
                if tail in [0,1,2,3,4] and n not in [11,22,33,44]:
                    group1.add(n)
                if tail in [5,6,7,8] and tail != 9:
                    group2.add(n)
            # 目标码列
            col = f'number{target_col}'
            if col not in sorted_data.columns:
                return {'error': f'未找到{col}列'}
            # 统计每期目标码属于哪组
            group_seq = []
            qishu_list = sorted_data['qishu'].tolist() if 'qishu' in sorted_data.columns else []
            target_number_list = sorted_data[col].tolist() if col in sorted_data.columns else []
            draw_time_list = sorted_data['draw_time'].tolist() if 'draw_time' in sorted_data.columns else []
            for num in sorted_data[col]:
                if num in group1:
                    group_seq.append(1)
                elif num in group2:
                    group_seq.append(2)
                else:
                    group_seq.append(0)  # 不属于任何组
            # 统计遗漏和连续命中（并记录每期的当前连中/遗漏）
            result = {'group1': {'miss': [], 'hit': []}, 'group2': {'miss': [], 'hit': []}}
            detail_rows = []
            g1_hit = g1_miss = g2_hit = g2_miss = 0
            for i, g in enumerate(group_seq):
                # 组1
                if g == 1:
                    g1_hit += 1
                    if g1_miss > 0:
                        result['group1']['miss'].append(g1_miss)
                        g1_miss = 0
                else:
                    g1_miss += 1
                    if g1_hit > 0:
                        result['group1']['hit'].append(g1_hit)
                        g1_hit = 0
                # 组2
                if g == 2:
                    g2_hit += 1
                    if g2_miss > 0:
                        result['group2']['miss'].append(g2_miss)
                        g2_miss = 0
                else:
                    g2_miss += 1
                    if g2_hit > 0:
                        result['group2']['hit'].append(g2_hit)
                        g2_hit = 0
                # 记录本期
                detail_rows.append({
                    'qishu': qishu_list[i] if i < len(qishu_list) else '',
                    'draw_time': str(draw_time_list[i]) if i < len(draw_time_list) else '',
                    'number': target_number_list[i] if i < len(target_number_list) else '',
                    'group': g,
                    'g1_hit': g1_hit if g == 1 else 0,
                    'g2_hit': g2_hit if g == 2 else 0,
                    'g1_miss': g1_miss if g != 1 else 0,
                    'g2_miss': g2_miss if g != 2 else 0
                })
            # 收尾
            if g1_miss > 0:
                result['group1']['miss'].append(g1_miss)
            if g1_hit > 0:
                result['group1']['hit'].append(g1_hit)
            if g2_miss > 0:
                result['group2']['miss'].append(g2_miss)
            if g2_hit > 0:
                result['group2']['hit'].append(g2_hit)
            # 当前期属于哪组
            current_group = group_seq[0] if group_seq else 0
            return {
                'group1_numbers': sorted(list(group1)),
                'group2_numbers': sorted(list(group2)),
                'target_col': col,
                'current_group': current_group,
                'group_seq': group_seq,
                'qishu_list': qishu_list,
                'target_number_list': target_number_list,
                'draw_time_list': draw_time_list,
                'result': result,
                'detail_rows': detail_rows
            }
        except Exception as e:
            print(f"自定义组合分析错误: {e}")
            return {'error': str(e)} 

    def get_seventh_digit_tens_analysis(self, position=7):
        """
        第N码十位组合分析：
        - 只分析numberN的十位
        - 分别统计 00,01,02,03,04,12,13,14,23,24,34 这11组的遗漏情况
        - 每期只要组合中包含当前十位数字的组合算命中，其他组合算遗漏
        - 统计每组的遗漏区段（长度）、最大遗漏、当前遗漏、遗漏前三名，返回每组明细和统计
        """
        if self.data.empty:
            return {}
        try:
            sorted_data = self.data.sort_values('qishu', ascending=True).reset_index(drop=True)
            col = f'number{position}'
            if col not in sorted_data.columns:
                return {'error': f'未找到{col}列'}
            qishu_list = sorted_data['qishu'].tolist() if 'qishu' in sorted_data.columns else []
            draw_time_list = sorted_data['draw_time'].tolist() if 'draw_time' in sorted_data.columns else []
            numberN_list = sorted_data[col].tolist() if col in sorted_data.columns else []
            # 严格提取十位，防止None/NaN等异常
            tens_list = []
            for n in numberN_list:
                try:
                    n_int = int(n)
                    ten = n_int // 10
                except Exception:
                    ten = None
                tens_list.append(ten)
            # 组合列表
            combs = ['00','01','02','03','04','12','13','14','23','24','34']
            group_stats = {}
            for comb in combs:
                miss_streaks = []
                current_miss = 0
                detail_rows = []
                a, b = int(comb[0]), int(comb[1])
                for i in range(len(tens_list)):
                    qishu = qishu_list[i] if i < len(qishu_list) else ''
                    draw_time = str(draw_time_list[i]) if i < len(draw_time_list) else ''
                    numN = numberN_list[i] if i < len(numberN_list) else ''
                    ten = tens_list[i]
                    # 命中逻辑：只要组合中包含当前十位数字
                    is_hit = (ten == a or ten == b)
                    if is_hit:
                        if current_miss > 0:
                            miss_streaks.append(current_miss)
                        current_miss = 0
                    else:
                        current_miss += 1
                    detail_rows.append({
                        'qishu': qishu,
                        'draw_time': draw_time,
                        'number': numN,
                        'tens': ten,
                        'is_hit': is_hit,
                        'miss_streak': current_miss if not is_hit else 0
                    })
                # 收尾
                if current_miss > 0:
                    miss_streaks.append(current_miss)
                # 最大遗漏、当前遗漏、遗漏前三名
                max_miss = max(miss_streaks + [current_miss]) if miss_streaks or current_miss > 0 else 0
                top3_miss = sorted(miss_streaks, reverse=True)[:3] if miss_streaks else []
                current_miss_count = current_miss
                group_stats[comb] = {
                    'detail_rows': detail_rows,
                    'miss_streaks': miss_streaks,
                    'max_miss': max_miss,
                    'top3_miss': top3_miss,
                    'current_miss': current_miss_count
                }
            return group_stats
        except Exception as e:
            print(f"第N码十位分析错误: {e}")
            return {'error': str(e)} 

    def get_sixplusminus_analysis(self, threshold=10, plusminus=1):
        """
        前6码±N推荐分析：
        - 每期取前6个码，对每个码加N和减N，超出49回到1，小于1回到49，得到12个推荐码（去重）
        - 判断下一期的第7个码是否在这12个推荐码中，有则命中，没有则为遗漏
        - 统计最大遗漏、当前遗漏、每期明细
        - 返回最新一期的12码推荐，支持高亮阀值
        """
        if self.data.empty:
            return {}
        try:
            sorted_data = self.data.sort_values('qishu', ascending=True).reset_index(drop=True)
            qishu_list = sorted_data['qishu'].tolist()
            draw_time_list = sorted_data['draw_time'].tolist() if 'draw_time' in sorted_data.columns else []
            n = len(sorted_data)
            miss_streaks = []
            current_miss = 0
            detail_rows = []
            max_miss = 0
            def plus_wrap(num, n):
                res = num + n
                while res > 49:
                    res -= 49
                return res
            def minus_wrap(num, n):
                res = num - n
                while res < 1:
                    res += 49
                return res
            # 记录每期的12码推荐和命中情况
            for i in range(n-1):
                nums = [int(sorted_data.iloc[i][f'number{j}']) for j in range(1,7)]
                pmset = set()
                for num in nums:
                    p = plus_wrap(num, plusminus)
                    m = minus_wrap(num, plusminus)
                    pmset.add(p)
                    pmset.add(m)
                pmset = sorted(list(pmset))
                next_seventh = int(sorted_data.iloc[i+1]['number7']) if i+1 < n else None
                is_hit = next_seventh in pmset if next_seventh is not None else None
                if is_hit:
                    if current_miss > 0:
                        miss_streaks.append(current_miss)
                    current_miss = 0
                else:
                    current_miss += 1
                detail_rows.append({
                    'qishu': qishu_list[i+1] if i+1 < n else '',
                    'draw_time': str(draw_time_list[i+1]) if i+1 < len(draw_time_list) else '',
                    'plusminus12': pmset,
                    'seventh': next_seventh,
                    'is_hit': is_hit,
                    'miss_streak': current_miss if not is_hit else 0
                })
            # 收尾
            if current_miss > 0:
                miss_streaks.append(current_miss)
            max_miss = max(miss_streaks) if miss_streaks else 0
            current_miss_count = current_miss
            # 最新一期的12码推荐
            latest_plusminus = []
            latest_six = []
            if n > 0:
                nums = [int(sorted_data.iloc[-1][f'number{j}']) for j in range(1,7)]
                latest_six = nums
                pmset = set()
                for num in nums:
                    p = plus_wrap(num, plusminus)
                    m = minus_wrap(num, plusminus)
                    pmset.add(p)
                    pmset.add(m)
                latest_plusminus = sorted(list(pmset))
            # 阀值高亮
            highlight = [num for num in latest_plusminus if miss_streaks and current_miss_count >= threshold]
            return {
                'max_miss': max_miss,
                'current_miss': current_miss_count,
                'detail_rows': detail_rows,
                'latest_plusminus': latest_plusminus,
                'latest_six': latest_six,
                'highlight': highlight,
                'threshold': threshold,
                'plusminus': plusminus
            }
        except Exception as e:
            print(f"前6码±N推荐分析错误: {e}")
            return {'error': str(e)} 

def solar_to_lunar(date_str):
    """
    新历日期字符串转农历（返回 dict: year, month, day, is_leap）
    支持 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM:SS'
    """
    try:
        from lunarcalendar import Converter, Solar
        if len(date_str) > 10:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        solar = Solar(dt.year, dt.month, dt.day)
        lunar = Converter.Solar2Lunar(solar)
        return {
            'year': lunar.year,
            'month': lunar.month,
            'day': lunar.day,
            'is_leap': getattr(lunar, 'isleap', False)
        }
    except Exception as e:
        print(f"solar_to_lunar error: {e}")
        return None 