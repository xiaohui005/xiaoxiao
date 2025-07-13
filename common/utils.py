#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
包含颜色处理、数据格式化等公共工具函数
"""

def get_number_color_class(num):
    """
    根据号码获取颜色类名
    
    Args:
        num (int): 号码
        
    Returns:
        str: 颜色类名 ('red', 'green', 'blue', '')
    """
    # 鲜红色球 - 1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46
    red_numbers = [1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]
    
    # 绿色球 - 3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48
    green_numbers = [3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]
    
    # 暗蓝色球 - 5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49
    blue_numbers = [5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49]
    
    if num in red_numbers:
        return 'red'
    elif num in green_numbers:
        return 'green'
    elif num in blue_numbers:
        return 'blue'
    else:
        return ''  # 默认颜色

def create_number_ball_html(num, size='normal'):
    """
    创建带颜色的号码球HTML
    
    Args:
        num (int): 号码
        size (str): 尺寸 ('small', 'normal', 'large')
        
    Returns:
        str: HTML字符串
    """
    color_class = get_number_color_class(num)
    
    # 根据尺寸设置样式
    if size == 'small':
        style = 'width: 25px; height: 25px; line-height: 25px; font-size: 12px;'
    elif size == 'large':
        style = 'width: 50px; height: 50px; line-height: 50px; font-size: 18px;'
    else:  # normal
        style = ''
    
    return f'<span class="lottery-number {color_class}" style="{style}">{num}</span>'

def format_date(date_obj):
    """
    格式化日期
    
    Args:
        date_obj: 日期对象
        
    Returns:
        str: 格式化后的日期字符串
    """
    if date_obj is None:
        return '-'
    
    try:
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return str(date_obj)
    except:
        return str(date_obj)

def format_numbers_list(numbers):
    """
    格式化号码列表
    
    Args:
        numbers (list): 号码列表
        
    Returns:
        str: 格式化后的HTML字符串
    """
    if not numbers:
        return ''
    
    html = ''
    for num in numbers:
        html += create_number_ball_html(num)
    return html

def get_chart_colors(numbers):
    """
    根据号码列表获取图表颜色
    
    Args:
        numbers (list): 号码列表
        
    Returns:
        list: 颜色列表
    """
    colors = []
    for num in numbers:
        color_class = get_number_color_class(int(num))
        if color_class == 'red':
            colors.append('rgba(255, 71, 87, 0.8)')
        elif color_class == 'green':
            colors.append('rgba(46, 213, 115, 0.8)')
        elif color_class == 'blue':
            colors.append('rgba(55, 66, 250, 0.8)')
        else:
            colors.append('rgba(102, 126, 234, 0.8)')  # 默认颜色
    
    return colors

def validate_number_range(num, min_val=1, max_val=49):
    """
    验证号码范围
    
    Args:
        num (int): 号码
        min_val (int): 最小值
        max_val (int): 最大值
        
    Returns:
        bool: 是否在有效范围内
    """
    try:
        num_int = int(num)
        return min_val <= num_int <= max_val
    except (ValueError, TypeError):
        return False

def group_data_by_year(data):
    """
    按年份分组数据
    
    Args:
        data (list): 数据列表
        
    Returns:
        dict: 按年份分组的数据
    """
    grouped = {}
    for item in data:
        if 'qishu' in item and item['qishu']:
            year = item['qishu'][:4]
            if year not in grouped:
                grouped[year] = []
            grouped[year].append(item)
    
    return grouped 