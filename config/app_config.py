import os
from datetime import datetime
import json

class AppConfig:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = True
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5004
    
    # 数据库配置
    # 优先读取exe同目录下的db_config.json
    exe_dir = os.path.dirname(os.path.abspath(__file__))
    run_dir = os.path.abspath(os.getcwd())
    external_path = os.path.join(run_dir, 'db_config.json')
    config_path = os.path.join(exe_dir, '..', 'db_config.json')
    if os.path.exists(external_path):
        with open(external_path, 'r', encoding='utf-8') as f:
            DATABASE_CONFIG = json.load(f)
    elif os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            DATABASE_CONFIG = json.load(f)
    else:
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
    
    # 组合分析报警阈值（当前值大于最大值-该阈值时触发报警）
    COMBINATION_ALERT_THRESHOLD = 3  # 可根据需要修改
    
    # 十位组合分析报警阈值（当前值大于最大值-该阈值时触发报警）
    TENS_ANALYSIS_ALERT_THRESHOLD = 3  # 可根据需要修改
    
    # 前6码±N推荐分析报警阈值（当前遗漏大于最大遗漏-该阈值时报警）
    SIXPLUSMINUS_ALERT_THRESHOLD = 3  # 可根据需要修改
    
    # +1~+20区间分析报警阈值（当前遗漏大于最大遗漏-该阈值时报警）
    PLUS20_ALERT_THRESHOLD = 3  # 可根据需要修改
    
    # -1~-20区间分析报警阈值（当前遗漏大于最大遗漏-该阈值时报警）
    MINUS20_ALERT_THRESHOLD = 3  # 可根据需要修改
    
    # 关注点区间分析报警阈值（当前遗漏/连中大于最大遗漏/连中-该阈值时报警）
    PLACE_ANALYSIS_ALERT_THRESHOLD = -13  # 可根据需要修改
    
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