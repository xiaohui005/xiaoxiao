# 彩票开奖数据分析系统 (优化版)

## 🚀 项目简介

这是一个基于 Flask 的彩票开奖数据分析系统，采用模块化架构设计，提供完整的开奖数据查询、统计分析和可视化功能。

## 📁 项目结构

```
sixnew6/
├── app_optimized.py          # 主应用入口
├── 
├── routes/                   # 路由模块
│   ├── __init__.py
│   ├── main_routes.py        # 主路由（主页、状态）
│   ├── data_routes.py        # 数据路由（数据获取、最近数据）
│   ├── statistics_routes.py  # 统计路由（统计、频率、冷热号码）
│   └── analysis_routes.py    # 分析路由（分析、趋势、组合）
├── 
├── config/                   # 配置模块
│   ├── __init__.py
│   └── app_config.py         # 应用配置管理
├── 
├── utils/                    # 工具模块
│   ├── __init__.py
│   └── api_helpers.py        # API辅助工具
├── 
├── common/                   # 通用模块
│   ├── __init__.py
│   ├── database_manager.py   # 数据库管理
│   ├── lottery_analyzer.py   # 数据分析器
│   ├── utils.py              # 通用工具
│   └── mock_data_generator.py # 模拟数据生成
├── 
├── templates/                # 前端模板
├── static/                   # 静态文件
├── 
├── shared_config.py          # 共享配置
├── requirements.txt          # 依赖包
└── README_OPTIMIZED.md       # 详细说明文档
```

## 🛠️ 技术栈

- **后端**: Flask, PyMySQL, Pandas, NumPy
- **前端**: Bootstrap, Chart.js, jQuery
- **数据库**: MySQL
- **架构**: 模块化设计，Flask Blueprint

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `config/app_config.py` 中的数据库配置：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',
    'database': 'lottery',
    'charset': 'utf8mb4'
}
```

### 3. 启动应用

```bash
python app_optimized.py
```

访问地址: http://localhost:5001

## 📊 功能特性

### 数据查询
- 开奖数据查询（支持分页、日期筛选）
- 最近开奖数据
- 系统状态检查

### 统计分析
- 基础统计信息
- 号码出现频率分析
- 冷热号码分析

### 数据分析
- 趋势分析
- 组合分析
- 奇偶、大小分析
- 号码范围分析

### 可视化
- 号码频率图表
- 趋势分析图表
- 响应式界面设计

## 🔧 API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 主页 |
| `/api/status` | GET | 系统状态 |
| `/api/data` | GET | 获取开奖数据 |
| `/api/recent` | GET | 最近开奖数据 |
| `/api/statistics` | GET | 统计数据 |
| `/api/analysis` | GET | 分析数据 |
| `/api/frequency` | GET | 号码频率 |
| `/api/hot-cold` | GET | 冷热号码 |
| `/api/trends` | GET | 趋势分析 |
| `/api/combinations` | GET | 组合分析 |

## 🏗️ 架构优势

### 模块化设计
- 路由按功能分组，便于维护
- 数据库和分析逻辑独立
- 配置集中管理

### 可扩展性
- 易于添加新功能
- 支持多环境配置
- 清晰的代码结构

### 可维护性
- 统一的错误处理
- 详细的日志记录
- 完整的文档说明

## 📝 开发说明

### 添加新功能
1. 在对应的路由模块中添加新端点
2. 在 `utils/api_helpers.py` 中添加通用函数
3. 在 `config/app_config.py` 中添加配置项

### 修改现有功能
1. 定位到对应的路由模块
2. 使用工具函数保持一致性
3. 更新配置如需要

## 🔒 安全特性

- 统一的错误处理避免信息泄露
- 配置验证防止无效设置
- 输入验证和清理
- 安全的默认配置

## 📈 性能优化

- 模块化加载减少内存占用
- 蓝图路由提高Flask性能
- 配置缓存减少重复计算
- 工具函数减少代码执行时间

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系开发者。

---

**注意**: 这是优化版系统，采用模块化架构，相比原版本具有更好的可维护性和可扩展性。 