# 彩票数据分析系统

一个基于Python Flask的Web应用，用于分析彩票数据库中number1~number6与下一期number7的关系，以及number7的自身规律。

## 功能特点

- 🔍 **数据分析**: 分析每期number1~6与下一期number7的关系
- 📊 **可视化展示**: 现代化的Web界面，直观显示分析结果
- 📅 **按年分组**: 支持按年份分组分析数据
- 📈 **统计图表**: 显示命中率、号码分布、出现间隔等统计信息
- 🔄 **实时更新**: 每5分钟自动刷新数据
- 📱 **响应式设计**: 支持手机、平板、电脑等多种设备

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL数据库已启动，并修改 `app.py` 中的数据库连接配置：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # 你的MySQL用户名
    'password': 'root',    # 你的MySQL密码
    'database': 'lottery',
    'charset': 'utf8mb4'
}
```

### 3. 启动应用

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

### 4. 访问系统

打开浏览器访问：http://localhost:5000

## 系统功能

### 总体统计
- 总记录数
- 命中次数
- 命中率
- 数据年份数量

### 按年份分析
- 每年开奖期数
- 每年命中次数
- 每年命中率
- 可视化进度条

### Number7分析
- 号码分布统计
- 出现间隔分析
- 可视化图表展示

### 关系分析
- 最近20期详细数据
- 本期号码与下期Number7关系
- 命中状态标识

## 文件结构

```
lottery-analysis/
├── app.py              # Flask主应用
├── run.py              # 启动脚本
├── requirements.txt    # Python依赖
├── README.md          # 项目说明
├── analyze_lottery.py # 命令行分析脚本
└── templates/
    └── index.html     # Web界面模板
```

## 数据库表结构

假设 `lottery_draws` 表结构如下：

```sql
CREATE TABLE lottery_draws (
    id INT PRIMARY KEY AUTO_INCREMENT,
    draw_date DATE,
    number1 INT,
    number2 INT,
    number3 INT,
    number4 INT,
    number5 INT,
    number6 INT,
    number7 INT
);
```

## 使用说明

1. **启动系统**: 运行 `python run.py`
2. **查看分析**: 访问 http://localhost:5000
3. **数据更新**: 系统每5分钟自动刷新数据
4. **停止系统**: 按 Ctrl+C

## 技术栈

- **后端**: Python Flask
- **数据库**: MySQL + PyMySQL
- **数据处理**: Pandas
- **前端**: Bootstrap 5 + JavaScript
- **图标**: Font Awesome

## 注意事项

- 确保MySQL服务正在运行
- 确保数据库连接配置正确
- 确保lottery_draws表存在且有数据
- 建议在生产环境中使用WSGI服务器部署

## 扩展功能

后续可以添加的功能：
- 更多统计图表（柱状图、折线图等）
- 数据导出功能
- 用户登录系统
- 历史数据对比
- 预测算法 