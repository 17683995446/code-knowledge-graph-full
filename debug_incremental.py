#!/usr/bin/env python3
"""详细调试增量更新问题"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_incremental_update():
    """详细调试增量更新问题"""
    
    print("=" * 80)
    print("详细调试增量更新问题")
    print("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建独立的数据库
        db_path = temp_path / 'debug.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        # 隔离全局数据库连接
        _isolate_database(db_conn)
        
        # 创建初始文件
        file1 = temp_path / "file1.py"
        file1.write_text("""
class InitialClass:
    def method1(self):
        return 1

def initial_func():
    return 2
""")
        
        print("\n--- 步骤1: 创建初始引擎并同步 ---")
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        stats = engine.full_sync()
        
        print(f"初始同步: {stats.files_processed}文件, {stats.types_processed}类型, {stats.functions_processed}函数")
        
        # 检查缓存
        print(f"缓存状态: {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        # 创建新文件（不修改旧文件）
        file2 = temp_path / "file2.py"
        file2.write_text("""
class NewClass:
    def new_method(self):
        return 3

def new_func():
    return 4
""")
        
        print("\n--- 步骤2: 添加新文件 ---")
        print(f"新文件: {file2}")
        print(f"文件存在: {file2.exists()}")
        
        # 使用增量更新
        print("\n调用 process_events...")
        update_stats = engine.process_events([file2])
        
        print(f"增量更新结果: {update_stats.files_processed}文件, {update_stats.types_processed}类型, {update_stats.functions_processed}函数")
        
        # 检查数据库
        print("\n--- 步骤3: 检查数据库 ---")
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_functions = FunctionDAO.get_all()
        
        print(f"数据库: {len(db_files)}文件, {len(db_types)}类型, {len(db_functions)}函数")
        print("文件列表:")
        for f in db_files:
            print(f"  - {f['path']} (id={f['id']})")
        
        # 检查缓存
        print("\n--- 步骤4: 检查内存缓存 ---")
        print(f"缓存: {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        print("类型缓存键:")
        for key in engine._type_cache:
            print(f"  - {key}")
        print("函数缓存键:")
        for key in engine._function_cache:
            print(f"  - {key}")
        
        # 一致性检查
        print("\n--- 步骤5: 一致性检查 ---")
        types_ok = len(engine._type_cache) == len(db_types)
        functions_ok = len(engine._function_cache) == len(db_functions)
        
        print(f"类型: 缓存={len(engine._type_cache)}, DB={len(db_types)} -> {'✓ PASS' if types_ok else '✗ FAIL'}")
        print(f"函数: 缓存={len(engine._function_cache)}, DB={len(db_functions)} -> {'✓ PASS' if functions_ok else '✗ FAIL'}")
        
        # 恢复全局连接
        _restore_database()
        
        print("\n" + "=" * 80)
        print("调试完成")
        print("=" * 80)


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
    debug_incremental_update()
