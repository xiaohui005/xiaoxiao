# 共享配置模块，避免循环导入

# 全局变量
DATABASE_AVAILABLE = False
db_manager = None

def set_database_status(status, manager=None):
    """设置数据库状态"""
    global DATABASE_AVAILABLE, db_manager
    DATABASE_AVAILABLE = status
    if manager:
        db_manager = manager

def get_database_status():
    """获取数据库状态"""
    return DATABASE_AVAILABLE

def get_db_manager():
    """获取数据库管理器"""
    return db_manager 