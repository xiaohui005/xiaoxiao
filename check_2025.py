from common.database_manager import DatabaseManager
from config.zodiac_config import get_zodiac_numbers_by_year

db = DatabaseManager()

# 检查2025199期的完整数据
print("=== 检查2025199期完整数据 ===")
full_199 = db.execute_query("SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7 FROM antapp_lotterydraw WHERE qishu = '2025199'")
if full_199:
    row = full_199[0]
    numbers = [row['number1'], row['number2'], row['number3'], row['number4'], row['number5'], row['number6'], row['number7']]
    print(f"2025199期开奖号码: {numbers}")
    
    # 检查2025年的生肖映射
    print("\n=== 2025年生肖映射 ===")
    year_2025_zodiac = {
        '鼠': [6, 18, 30, 42],
        '牛': [5, 17, 29, 41],
        '虎': [4, 16, 28, 40],
        '兔': [3, 15, 27, 39],
        '龙': [2, 14, 26, 38],
        '蛇': [1, 13, 25, 37, 49],
        '马': [12, 24, 36, 48],
        '羊': [11, 23, 35, 47],
        '猴': [10, 22, 34, 46],
        '鸡': [9, 21, 33, 45],
        '狗': [8, 20, 32, 44],
        '猪': [7, 19, 31, 43]
    }
    
    # 检查每个号码对应的生肖
    for num in numbers:
        for zodiac, zodiac_numbers in year_2025_zodiac.items():
            if num in zodiac_numbers:
                print(f"号码 {num} -> {zodiac}")
                break
else:
    print("未找到2025199期完整数据")

# 测试API查询逻辑（包含生肖筛选）
print("\n=== 测试API查询逻辑（包含生肖筛选） ===")
year = "2025"
limit = 200
zodiac = "all"

# 构建查询条件（模拟API逻辑）
where_conditions = []
params = []

if year != 'all':
    where_conditions.append("qishu LIKE %s")
    params.append(f"{year}%")

# 生肖筛选逻辑
zodiac_numbers = {}
if year != 'all' and year.isdigit():
    year_int = int(year)
    for zodiac_name in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']:
        numbers = get_zodiac_numbers_by_year(year_int, zodiac_name)
        if numbers:
            zodiac_numbers[zodiac_name] = numbers
else:
    zodiac_numbers = {
        '鼠': [6, 18, 30, 42],
        '牛': [5, 17, 29, 41],
        '虎': [4, 16, 28, 40],
        '兔': [3, 15, 27, 39],
        '龙': [2, 14, 26, 38],
        '蛇': [1, 13, 25, 37, 49],
        '马': [12, 24, 36, 48],
        '羊': [11, 23, 35, 47],
        '猴': [10, 22, 34, 46],
        '鸡': [9, 21, 33, 45],
        '狗': [8, 20, 32, 44],
        '猪': [7, 19, 31, 43]
    }

if zodiac != 'all' and zodiac in zodiac_numbers:
    numbers = zodiac_numbers[zodiac]
    placeholders = ','.join(['%s'] * len(numbers))
    where_conditions.append(f"(number1 IN ({placeholders}) OR number2 IN ({placeholders}) OR number3 IN ({placeholders}) OR number4 IN ({placeholders}) OR number5 IN ({placeholders}) OR number6 IN ({placeholders}) OR number7 IN ({placeholders}))")
    params.extend(numbers * 7)

where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

print(f"WHERE条件: {where_clause}")
print(f"参数: {params}")

# 执行查询
query = f"""
    SELECT qishu, draw_time, number1, number2, number3, number4, number5, number6, number7
    FROM antapp_lotterydraw 
    WHERE {where_clause}
    ORDER BY qishu DESC 
    LIMIT %s
"""
params.append(limit)

api_result = db.execute_query(query, params)
print(f"API查询结果数量: {len(api_result)}")
if api_result:
    print(f"API查询第一条: {api_result[0]['qishu']}")
    print(f"API查询最后一条: {api_result[-1]['qishu']}")

# 检查API结果中是否有2025199期
has_199 = any(row['qishu'] == '2025199' for row in api_result)
print(f"API结果是否包含2025199期: {has_199}") 