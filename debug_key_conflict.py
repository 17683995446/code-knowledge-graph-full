#!/usr/bin/env python3
"""详细调试缓存键冲突"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_cache_key_conflict():
    """调试缓存键冲突"""
    
    print("=" * 80)
    print("详细调试缓存键冲突")
    print("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建独立的数据库
        db_path = temp_path / 'test.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        # 隔离全局数据库连接
        _isolate_database(db_conn)
        
        # 创建两个有相同函数名的文件
        file1 = temp_path / "file1.py"
        file1.write_text("""
class TestClass:
    def process(self):
        return 1
""")
        
        file2 = temp_path / "file2.py"
        file2.write_text("""
def process():
    return 2
""")
        
        # 初始化引擎
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        # 全量同步
        print("\n--- 全量同步 ---")
        stats = engine.full_sync()
        
        # 检查数据库中的函数
        print("\n数据库中的函数:")
        db_functions = FunctionDAO.get_all()
        for f in db_functions:
            key = f"{f['name']}:{f['type_id']}:{f['file_id']}"
            print(f"  {key} -> {f}")
        
        # 检查缓存
        print("\n缓存中的函数:")
        for key, val in engine._function_cache.items():
            print(f"  {key} -> id={val['id']}")
        
        # 检查是否一致
        print("\n--- 一致性检查 ---")
        db_func_keys = {f"{f['name']}:{f['type_id']}:{f['file_id']}" for f in db_functions}
        cache_func_keys = set(engine._function_cache.keys())
        
        print(f"数据库中的键: {len(db_func_keys)}")
        print(f"缓存中的键: {len(cache_func_keys)}")
        
        missing_in_cache = db_func_keys - cache_func_keys
        extra_in_cache = cache_func_keys - db_func_keys
        
        if missing_in_cache:
            print(f"\n数据库有但缓存没有的:")
            for key in missing_in_cache:
                print(f"  {key}")
        
        if extra_in_cache:
            print(f"\n缓存有但数据库没有的:")
            for key in extra_in_cache:
                print(f"  {key}")
        
        # 恢复全局连接
        _restore_database()


def _isolate_database(db_conn):
    """隔离全局数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    _isolate_database.original_db = src.database.DATABASE_CONNECTION
    _isolate_database.original_dao_db = dao_module.DATABASE_CONNECTION
    
    src.database.DATABASE_CONNECTION = db_conn
    dao_module.DATABASE_CONNECTION = db_conn


def _restore_database():
    """恢复全局数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    src.database.DATABASE_CONNECTION = _isolate_database.original_db
    dao_module.DATABASE_CONNECTION = _isolate_database.original_dao_db


if __name__ == "__main__":
    debug_cache_key_conflict()
