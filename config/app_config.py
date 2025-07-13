import os
from datetime import datetime

class AppConfig:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = True
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5001
    
    # 数据库配置
    DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'lottery',
        'charset': 'utf8mb4'
    }
    
    # API配置
    API_PREFIX = '/api'
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 1000
    
    # 分析配置
    ANALYSIS_DAYS = 30
    FREQUENCY_LIMIT = 1000
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_database_url(cls):
        """获取数据库连接URL"""
        config = cls.DATABASE_CONFIG
        return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    
    @classmethod
    def get_startup_message(cls):
        """获取启动消息"""
        return f"""
🚀 彩票开奖数据分析系统 (优化版) 启动中...
✅ 数据库连接正常
📊 使用真实数据库数据
🌐 访问地址: http://localhost:{cls.PORT}
⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """ 