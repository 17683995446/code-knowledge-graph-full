#!/usr/bin/env python3
"""调试增量更新中的缓存问题"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_cache_gap():
    """调试缓存与数据库的差距"""
    
    print("=" * 80)
    print("调试缓存与数据库的差距")
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
        for i in range(3):
            file = temp_path / f"file{i}.py"
            file.write_text(f"""
class Class{i}:
    def method{i}(self):
        return {i}

def func{i}():
    return {i}
""")
        
        print("\n--- 步骤1: 初始化并同步 ---")
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        stats = engine.full_sync()
        
        print(f"同步后:")
        print(f"  DB: {len(FileDAO.get_all())}文件, {len(TypeDAO.get_all())}类型, {len(FunctionDAO.get_all())}函数")
        print(f"  Cache: {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        # 创建新文件
        new_file = temp_path / "new_file.py"
        new_file.write_text("""
class NewClass:
    def new_method(self):
        return 1

def new_func():
    return 2
""")
        
        print("\n--- 步骤2: 添加新文件 ---")
        print(f"新文件: {new_file}")
        
        # 增量更新
        update_stats = engine.process_events([new_file])
        
        print(f"更新统计:")
        print(f"  files_processed: {update_stats.files_processed}")
        print(f"  types_processed: {update_stats.types_processed}")
        print(f"  functions_processed: {update_stats.functions_processed}")
        
        # 检查缓存
        print(f"\n--- 步骤3: 检查缓存 ---")
        print(f"文件缓存: {len(engine._file_id_cache)}")
        for k, v in engine._file_id_cache.items():
            print(f"  {k} -> {v}")
        
        print(f"\n类型缓存: {len(engine._type_cache)}")
        for k, v in engine._type_cache.items():
            print(f"  {k} -> id={v['id']}")
        
        print(f"\n函数缓存: {len(engine._function_cache)}")
        for k, v in engine._function_cache.items():
            print(f"  {k} -> id={v['id']}")
        
        # 检查数据库
        print(f"\n--- 步骤4: 检查数据库 ---")
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_functions = FunctionDAO.get_all()
        
        print(f"数据库文件: {len(db_files)}")
        for f in db_files:
            print(f"  {f['path']} (id={f['id']})")
        
        print(f"\n数据库类型: {len(db_types)}")
        for t in db_types:
            print(f"  {t['name']} (file_id={t['file_id']})")
        
        print(f"\n数据库函数: {len(db_functions)}")
        for f in db_functions:
            print(f"  {f['name']} (type_id={f['type_id']}, file_id={f['file_id']})")
        
        # 找出差异
        print(f"\n--- 步骤5: 分析差异 ---")
        
        # 找出数据库有但缓存没有的函数
        cache_func_keys = set(engine._function_cache.keys())
        db_func_keys = {f"{f['name']}:{f['type_id']}:{f['file_id']}" for f in db_functions}
        
        missing_in_cache = db_func_keys - cache_func_keys
        extra_in_cache = cache_func_keys - db_func_keys
        
        print(f"数据库有但缓存没有的函数: {len(missing_in_cache)}")
        for key in missing_in_cache:
            print(f"  {key}")
        
        print(f"\n缓存有但数据库没有的函数: {len(extra_in_cache)}")
        for key in extra_in_cache:
            print(f"  {key}")
        
        # 最终结论
        print(f"\n--- 结论 ---")
        types_ok = len(engine._type_cache) == len(db_types)
        functions_ok = len(engine._function_cache) == len(db_functions)
        print(f"类型: DB={len(db_types)}, Cache={len(engine._type_cache)} -> {'✓ PASS' if types_ok else '✗ FAIL'}")
        print(f"函数: DB={len(db_functions)}, Cache={len(engine._function_cache)} -> {'✓ PASS' if functions_ok else '✗ FAIL'}")
        
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
    debug_cache_gap()
