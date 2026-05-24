#!/usr/bin/env python3
"""调试快速连续修改问题"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_rapid_modifications():
    """调试快速连续修改问题"""
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        db_path = temp_path / 'debug.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        _isolate_database(db_conn)
        
        test_file = temp_path / "rapid.py"
        test_file.write_text("class Initial:\n    pass")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats = engine.full_sync()
        print(f"初始同步: {stats.files_processed}文件")
        
        print("\n前10次修改的详细日志:")
        for i in range(10):
            test_file.write_text(f"""
class Version{i}:
    def method_{i}(self):
        return {i}

def func_{i}():
    return {i}

def func_{i}_2(x):
    return x * {i}
""")
            
            # 检查文件信息
            stat = test_file.stat()
            print(f"  修改 {i}: mtime = {stat.st_mtime}, size = {stat.st_size}")
            
            # 调用增量更新
            stats = engine.process_events([test_file])
            print(f"          结果 = {stats.files_processed}文件, {stats.types_processed}类型")
            
            # 检查缓存
            if test_file in engine._file_id_cache:
                cached_id = engine._file_id_cache[test_file]
                print(f"          缓存ID = {cached_id}")
        
        # 检查文件是否在监控范围内
        print(f"\n文件监控范围: {engine._root_path}")
        print(f"测试文件: {test_file}")
        print(f"文件是否在监控范围: {test_file.is_relative_to(engine._root_path)}")
        
        _restore_database()


def _isolate_database(db_conn):
    """隔离数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    _isolate_database.original_db = src.database.DATABASE_CONNECTION
    _isolate_database.original_dao_db = dao_module.DATABASE_CONNECTION
    
    src.database.DATABASE_CONNECTION = db_conn
    dao_module.DATABASE_CONNECTION = db_conn


def _restore_database():
    """恢复数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    src.database.DATABASE_CONNECTION = _isolate_database.original_db
    dao_module.DATABASE_CONNECTION = _isolate_database.original_dao_db


if __name__ == "__main__":
    debug_rapid_modifications()
