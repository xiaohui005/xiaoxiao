# 本地资源使用说明

本项目已经将所有外部CDN资源下载到本地，确保在没有网络连接的情况下也能正常运行。

## 下载的资源文件

### CSS 文件
- `static/css/bootstrap.min.css` - Bootstrap 5.1.3 样式文件
- `static/css/font-awesome-local.css` - Font Awesome 6.0.0 图标样式文件（已修改字体路径）
- `static/css/icons.css` - 自定义图标样式文件

### JavaScript 文件
- `static/js/bootstrap.bundle.min.js` - Bootstrap 5.1.3 JavaScript 文件
- `static/js/chart.js` - Chart.js 图表库

### 字体文件
- `static/fonts/webfonts/fa-solid-900.woff2` - Font Awesome 实心图标字体
- `static/fonts/webfonts/fa-regular-400.woff2` - Font Awesome 常规图标字体
- `static/fonts/webfonts/fa-brands-400.woff2` - Font Awesome 品牌图标字体

### 图标文件
- `static/icons/svg/` - 自定义SVG图标集合
  - `home.svg` - 首页图标
  - `chart-line.svg` - 图表图标
  - `database.svg` - 数据库图标
  - `settings.svg` - 设置图标
  - `user.svg` - 用户图标
  - `calendar.svg` - 日历图标
  - `clock.svg` - 时钟图标
  - `chart-bar.svg` - 柱状图图标
  - `chart-pie.svg` - 饼图图标
  - `fire.svg` - 火焰图标
  - `trending-up.svg` - 趋势图标
  - `puzzle.svg` - 拼图图标
  - `table.svg` - 表格图标
  - `search.svg` - 搜索图标
  - `sync.svg` - 同步图标
  - `percentage.svg` - 百分比图标
  - `info.svg` - 信息图标

## 文件结构

```
static/
├── css/
│   ├── bootstrap.min.css
│   ├── font-awesome-local.css
│   └── icons.css
├── js/
│   ├── bootstrap.bundle.min.js
│   └── chart.js
├── fonts/
│   └── webfonts/
│       ├── fa-solid-900.woff2
│       ├── fa-regular-400.woff2
│       └── fa-brands-400.woff2
└── icons/
    ├── icon-demo.html
    └── svg/
        ├── home.svg
        ├── chart-line.svg
        ├── database.svg
        ├── settings.svg
        ├── user.svg
        ├── calendar.svg
        ├── clock.svg
        ├── chart-bar.svg
        ├── chart-pie.svg
        ├── fire.svg
        ├── trending-up.svg
        ├── puzzle.svg
        ├── table.svg
        ├── search.svg
        ├── sync.svg
        ├── percentage.svg
        └── info.svg
```

## 修改说明

### HTML 文件修改
在 `templates/index.html` 中，所有外部CDN链接已替换为本地文件：

```html
<!-- 原来的CDN链接 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

<!-- 修改为本地文件 -->
<link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/font-awesome-local.css') }}" rel="stylesheet">
<link href="{{ url_for('static', filename='css/icons.css') }}" rel="stylesheet">
<script src="{{ url_for('static', filename='js/chart.js') }}"></script>
<script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
```

### Font Awesome 字体路径修改
由于Font Awesome CSS文件中的字体路径是相对路径，我们创建了一个修改版本 `font-awesome-local.css`，将所有字体路径从 `../webfonts/` 修改为 `../fonts/webfonts/`。

### 自定义图标系统
新增了完整的自定义图标系统，包括：
- 17个SVG图标文件
- 完整的图标CSS样式系统
- 图标演示页面
- 详细的使用文档

## 图标使用

### Font Awesome 图标
```html
<i class="fas fa-home"></i>
<i class="fas fa-chart-line"></i>
<i class="fas fa-database"></i>
```

### SVG 图标
```html
<svg class="icon icon-primary">
    <use href="{{ url_for('static', filename='icons/svg/home.svg') }}"></use>
</svg>
```

## 测试

可以使用以下文件来测试所有本地资源是否正常工作：

1. **`test_local_resources.html`** - 基础资源测试页面
2. **`static/icons/icon-demo.html`** - 图标演示页面

在浏览器中打开这些文件，应该能看到：

1. Bootstrap 样式正常显示（按钮、警告框等）
2. Font Awesome 图标正常显示
3. 自定义SVG图标正常显示
4. Chart.js 图表正常渲染

## 优势

1. **离线运行**：不需要网络连接即可正常运行
2. **加载速度**：本地文件加载更快，不依赖外部CDN
3. **稳定性**：避免CDN服务不可用的风险
4. **版本控制**：确保使用特定版本的库文件
5. **丰富的图标**：提供Font Awesome和自定义SVG两种图标系统
6. **灵活定制**：SVG图标可以轻松修改颜色和大小

## 注意事项

1. 如果需要更新这些库文件，需要重新下载并替换相应文件
2. 确保 `static` 目录结构保持不变，否则字体文件路径会失效
3. 在生产环境中，建议对这些静态文件进行压缩和缓存优化
4. SVG图标使用 `currentColor` 来继承父元素的颜色，便于主题定制
5. 所有图标都支持响应式设计

## 相关文档

- `README_ICONS.md` - 详细的图标使用说明
- `static/icons/icon-demo.html` - 图标演示页面 