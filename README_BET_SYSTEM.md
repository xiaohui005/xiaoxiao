# 彩票投注管理系统使用说明

## 功能概述

本系统新增了关注点登记和投注历史数据分析功能，帮助用户更好地管理投注记录和分析投注效果。

## 新增功能

### 1. 关注点登记系统

#### 功能特点：
- **添加关注点**：可以自定义添加各种投注关注点
- **登记投注记录**：按期数记录投注信息
- **投注金额管理**：记录每次投注的金额
- **结果判断**：标记投注是否正确（打钩为对，不勾选为错）
- **数据管理**：支持删除和编辑功能
- **编辑功能**：支持修改已登记的关注点和投注记录

#### 使用方法：
1. 点击首页的"关注点登记"按钮进入系统
2. 在左侧添加新的关注点（如：号码间隔分析、第七码推荐等）
3. 在右侧登记投注记录，包括：
   - 选择关注点
   - 输入期数
   - 填写投注金额
   - 选择是否正确
4. 查看和管理已添加的关注点和投注记录

### 2. 历史数据分析系统

#### 功能特点：
- **年度分析**：按年份分析投注效果
- **连对连错分析**：统计最长连对和连错记录
- **正确率统计**：计算各关注点的预测准确率
- **收益分析**：计算投注净收益
- **数据筛选**：支持按年份和关注点筛选数据

#### 使用方法：
1. 点击首页的"历史数据分析"按钮进入系统
2. 选择要分析的年份和关注点
3. 查看总体统计信息
4. 分析最长连对连错记录
5. 查看年度详细分析
6. 导出分析数据

## 数据库结构

### places表（关注点表）
```sql
CREATE TABLE places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '关注点名称',
    description TEXT COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_name (name)
);
```

### bets表（投注记录表）
```sql
CREATE TABLE bets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    place_id INT NOT NULL COMMENT '关注点ID',
    qishu VARCHAR(20) NOT NULL COMMENT '期数',
    bet_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '投注金额',
    is_correct TINYINT(1) DEFAULT NULL COMMENT '是否正确：1-正确，0-错误，NULL-未判断',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    UNIQUE KEY unique_place_qishu (place_id, qishu)
);
```

## 安装和初始化

### 1. 运行数据库初始化脚本
```bash
python init_database.py
```

### 2. 启动应用程序
```bash
python app.py
```

### 3. 访问系统
打开浏览器访问：`http://localhost:5000`

## API接口说明

### 关注点相关API

#### 获取所有关注点
```
GET /api/places
```

#### 添加关注点
```
POST /api/places
Content-Type: application/json

{
    "name": "关注点名称",
    "description": "描述信息"
}
```

#### 删除关注点
```
DELETE /api/places/{place_id}
```

#### 更新关注点
```
PUT /api/places/{place_id}
Content-Type: application/json

{
    "name": "新的关注点名称",
    "description": "新的描述信息"
}
```

#### 获取单个关注点
```
GET /api/places/{place_id}
```

### 投注记录相关API

#### 获取所有投注记录
```
GET /api/bets
```

#### 添加投注记录
```
POST /api/bets
Content-Type: application/json

{
    "place_id": 1,
    "qishu": "20250101",
    "bet_amount": 100.00,
    "is_correct": 1
}
```

#### 删除投注记录
```
DELETE /api/bets/{bet_id}
```

#### 更新投注记录
```
PUT /api/bets/{bet_id}
Content-Type: application/json

{
    "place_id": 1,
    "qishu": "20250101",
    "bet_amount": 150.00,
    "is_correct": 1
}
```

#### 获取单个投注记录
```
GET /api/bets/{bet_id}
```

### 数据分析相关API

#### 获取年份列表
```
GET /api/bet-analysis/years
```

#### 获取分析数据
```
GET /api/bet-analysis/data?year=2025&place_id=1
```

## 使用示例

### 1. 添加关注点
1. 进入关注点登记页面
2. 在左侧表单中填写：
   - 关注点名称：号码间隔分析
   - 描述：基于号码间隔规律的投注点
3. 点击"添加关注点"按钮

### 2. 登记投注记录
1. 在右侧表单中填写：
   - 选择关注点：号码间隔分析
   - 期数：20250101
   - 投注金额：100
   - 是否正确：正确
2. 点击"登记记录"按钮

### 3. 编辑记录
1. **编辑关注点**：
   - 点击关注点列表中的"编辑"按钮
   - 修改名称和描述
   - 点击"更新关注点"按钮
   - 或点击"取消编辑"按钮取消

2. **编辑投注记录**：
   - 点击投注记录列表中的"编辑"按钮
   - 修改关注点、期数、投注金额或结果
   - 点击"更新记录"按钮
   - 或点击"取消编辑"按钮取消

### 4. 查看分析结果
1. 进入历史数据分析页面
2. 选择年份：2025
3. 查看统计信息：
   - 总记录数
   - 正确次数
   - 错误次数
   - 正确率
4. 查看最长连对连错记录
5. 查看年度详细分析

## 注意事项

1. **期数格式**：建议使用YYYYMMDD格式，系统会自动识别年份
2. **投注金额**：支持小数，如100.50
3. **结果判断**：及时标记投注结果，便于后续分析
4. **数据备份**：定期导出重要数据
5. **唯一性约束**：同一关注点在同一期数只能有一条记录

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 确认数据库连接配置是否正确

2. **表不存在**
   - 运行 `python init_database.py` 初始化数据库

3. **页面无法访问**
   - 确认Flask应用是否正常启动
   - 检查端口是否被占用

4. **数据不显示**
   - 检查数据库中是否有数据
   - 确认API接口是否正常返回数据

### 联系支持

如遇到其他问题，请检查：
1. 控制台错误信息
2. 数据库日志
3. 网络连接状态 