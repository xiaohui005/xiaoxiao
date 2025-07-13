# 图标资源使用说明

本项目包含了丰富的图标资源，包括Font Awesome图标和自定义SVG图标。

## 图标类型

### 1. Font Awesome 图标
- **位置**: `static/css/font-awesome-local.css`
- **字体文件**: `static/fonts/webfonts/`
- **使用方式**: `<i class="fas fa-icon-name"></i>`

### 2. 自定义SVG图标
- **位置**: `static/icons/svg/`
- **样式文件**: `static/css/icons.css`
- **使用方式**: `<svg class="icon"><use href="path/to/icon.svg"></use></svg>`

## 可用的SVG图标

### 基础图标
- `home.svg` - 首页图标
- `user.svg` - 用户图标
- `settings.svg` - 设置图标
- `database.svg` - 数据库图标

### 图表图标
- `chart-line.svg` - 折线图
- `chart-bar.svg` - 柱状图
- `chart-pie.svg` - 饼图
- `trending-up.svg` - 趋势上升

### 数据图标
- `calendar.svg` - 日历
- `clock.svg` - 时钟
- `table.svg` - 表格
- `search.svg` - 搜索

### 分析图标
- `fire.svg` - 火焰/热号
- `puzzle.svg` - 拼图/组合
- `percentage.svg` - 百分比
- `info.svg` - 信息
- `sync.svg` - 同步

## 图标样式类

### 尺寸类
- `.icon-sm` - 小尺寸 (0.875em)
- `.icon` - 默认尺寸 (1em)
- `.icon-lg` - 大尺寸 (1.33em)
- `.icon-xl` - 超大尺寸 (1.5em)
- `.icon-2x` - 2倍尺寸 (2em)
- `.icon-3x` - 3倍尺寸 (3em)

### 颜色类
- `.icon-primary` - 主要色 (#007bff)
- `.icon-success` - 成功色 (#28a745)
- `.icon-info` - 信息色 (#17a2b8)
- `.icon-warning` - 警告色 (#ffc107)
- `.icon-danger` - 危险色 (#dc3545)
- `.icon-light` - 浅色 (#f8f9fa)
- `.icon-dark` - 深色 (#343a40)

### 特殊颜色类
- `.icon-lottery` - 彩票色 (#e74c3c)
- `.icon-chart` - 图表色 (#3498db)
- `.icon-data` - 数据色 (#2ecc71)
- `.icon-analysis` - 分析色 (#f39c12)

### 动画类
- `.icon-spin` - 旋转动画
- `.icon-pulse` - 脉冲动画

### 背景类
- `.icon-bg` - 基础背景
- `.icon-bg-primary` - 主要背景
- `.icon-bg-success` - 成功背景
- `.icon-bg-info` - 信息背景
- `.icon-bg-warning` - 警告背景
- `.icon-bg-danger` - 危险背景

### 边框类
- `.icon-border` - 边框样式

## 使用示例

### Font Awesome 图标
```html
<!-- 基础使用 -->
<i class="fas fa-home"></i>
<i class="fas fa-chart-line"></i>
<i class="fas fa-database"></i>

<!-- 带尺寸 -->
<i class="fas fa-home fa-lg"></i>
<i class="fas fa-chart-line fa-2x"></i>

<!-- 带动画 -->
<i class="fas fa-sync fa-spin"></i>
<i class="fas fa-sync fa-pulse"></i>
```

### SVG 图标
```html
<!-- 基础使用 -->
<svg class="icon">
    <use href="{{ url_for('static', filename='icons/svg/home.svg') }}"></use>
</svg>

<!-- 带尺寸和颜色 -->
<svg class="icon icon-lg icon-primary">
    <use href="{{ url_for('static', filename='icons/svg/chart-line.svg') }}"></use>
</svg>

<!-- 带背景 -->
<svg class="icon icon-bg icon-bg-success">
    <use href="{{ url_for('static', filename='icons/svg/check.svg') }}"></use>
</svg>

<!-- 带动画 -->
<svg class="icon icon-spin">
    <use href="{{ url_for('static', filename='icons/svg/sync.svg') }}"></use>
</svg>
```

### 图标列表
```html
<ul class="icon-list">
    <li>
        <svg class="icon icon-primary">
            <use href="{{ url_for('static', filename='icons/svg/home.svg') }}"></use>
        </svg>
        <span>首页</span>
    </li>
    <li>
        <svg class="icon icon-chart">
            <use href="{{ url_for('static', filename='icons/svg/chart-line.svg') }}"></use>
        </svg>
        <span>图表</span>
    </li>
</ul>
```

## 在项目中的使用

### 导航标签
```html
<li class="nav-item">
    <a class="nav-link" href="#overview">
        <i class="fas fa-home"></i> 概览
    </a>
</li>
```

### 统计卡片
```html
<div class="stats-card">
    <h3><i class="fas fa-list"></i> 总期数</h3>
    <div class="number">1234</div>
</div>
```

### 按钮
```html
<button class="btn btn-primary">
    <i class="fas fa-search"></i> 查询数据
</button>
```

## 响应式图标

在小屏幕设备上，可以使用 `.icon-responsive` 类来调整图标大小：

```html
<svg class="icon icon-responsive">
    <use href="{{ url_for('static', filename='icons/svg/home.svg') }}"></use>
</svg>
```

## 自定义图标

要添加新的SVG图标：

1. 在 `static/icons/svg/` 目录下创建新的SVG文件
2. 确保SVG文件使用 `viewBox="0 0 24 24"` 和 `fill="currentColor"`
3. 在HTML中使用 `<use>` 标签引用图标

## 演示页面

可以访问 `static/icons/icon-demo.html` 来查看所有图标的演示效果。

## 注意事项

1. SVG图标使用 `currentColor` 来继承父元素的颜色
2. Font Awesome图标可以通过CSS类来改变颜色和大小
3. 所有图标都支持响应式设计
4. 图标文件已经本地化，不依赖外部CDN 