from flask import Flask
import traceback
import threading
import sys
import os
import webbrowser

# 托盘相关
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

# 修正模板和静态目录（兼容PyInstaller打包）
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    template_folder = os.path.join(base_dir, 'templates')
    static_folder = os.path.join(base_dir, 'static')
else:
    template_folder = 'templates'
    static_folder = 'static'

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

def create_image():
    # 生成一个简单的图标
    image = Image.new('RGB', (64, 64), color=(76, 75, 162))
    d = ImageDraw.Draw(image)
    d.ellipse((8, 8, 56, 56), fill=(102, 126, 234))
    d.text((18, 22), '彩', fill=(255,255,255))
    return image

def run_flask():
    app.run(debug=False, host='0.0.0.0', port=5004)

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

def on_open_site(icon, item):
    webbrowser.open(f"http://127.0.0.1:{AppConfig.PORT}")

# 导入配置和数据库管理
try:
    from config.app_config import AppConfig
    from common.database_manager import DatabaseManager
    from common.lottery_analyzer import LotteryAnalyzer
    from shared_config import set_database_status, get_database_status
    
    # 初始化Flask应用
    # app = Flask(__name__) # This line is now redundant as app is initialized above
    app.config.from_object(AppConfig)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager()
    
    # 测试数据库连接
    try:
        test_connection = db_manager.get_connection()
        test_connection.close()
        set_database_status(True, db_manager)
        print("✅ 数据库连接成功")
    except Exception as e:
        set_database_status(False)
        print(f"⚠️ 数据库连接失败: {e}")
        print("💡 请检查数据库配置或使用演示版本")
        
except ImportError as e:
    set_database_status(False)
    print(f"⚠️ 模块导入失败: {e}")
    print("💡 请检查依赖安装")

# 导入路由模块
from routes.main_routes import main_bp
from routes.data_routes import data_bp
from routes.analysis_routes import analysis_bp
from routes.statistics_routes import statistics_bp

# 注册蓝图
app.register_blueprint(main_bp)
app.register_blueprint(data_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(statistics_bp, url_prefix='/api')

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return {'error': '接口不存在'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': '服务器内部错误'}, 500

if __name__ == '__main__':
    print("🚀 彩票开奖数据分析系统 (优化版) 启动中...")
    if get_database_status():
        print("✅ 数据库连接正常")
        print("📊 使用真实数据库数据")
    else:
        print("⚠️ 数据库连接失败")
        print("💡 建议使用演示版本: python app_demo.py")
    print(f"🌐 访问地址: http://localhost:{AppConfig.PORT}")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    if pystray and Image:
        icon = pystray.Icon(
            "开奖分析系统",
            create_image(),
            "开奖分析系统",
            menu=pystray.Menu(
                pystray.MenuItem('打开网站', on_open_site),
                pystray.MenuItem('退出', on_exit)
            )
        )
        icon.run()
    else:
        print("未安装pystray/pillow，直接运行Flask。按Ctrl+C退出。")
        flask_thread.join() 