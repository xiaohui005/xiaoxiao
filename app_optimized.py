from flask import Flask
import traceback

# 导入配置和数据库管理
try:
    from config.app_config import AppConfig
    from common.database_manager import DatabaseManager
    from common.lottery_analyzer import LotteryAnalyzer
    from shared_config import set_database_status, get_database_status
    
    # 初始化Flask应用
    app = Flask(__name__)
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
    print("🌐 访问地址: http://localhost:5002")
    app.run(debug=True, host='0.0.0.0', port=5003) 