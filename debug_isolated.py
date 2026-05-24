#!/usr/bin/env python3
"""完全隔离的缓存一致性测试"""

import sys
import tempfile
import os
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import CONFIG
from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def isolated_cache_test():
    """在完全隔离的环境中测试缓存一致性"""
    
    print("=" * 80)
    print("完全隔离的缓存一致性测试")
    print("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建独立的数据库路径
        db_path = temp_path / 'isolated_test.db'
        
        # 创建测试文件
        test_file = temp_path / "test_module.py"
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1

def function1():
    return 2
""")
        
        print(f"\n测试环境:")
        print(f"  临时目录: {temp_path}")
        print(f"  数据库路径: {db_path}")
        print(f"  测试文件: {test_file}")
        
        # 创建新的数据库连接
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        # 修改全局的 DATABASE_CONNECTION（这是一个全局单例）
        import src.database
        original_db = src.database.DATABASE_CONNECTION
        src.database.DATABASE_CONNECTION = db_conn
        
        # 还需要修改各个 DAO 引用的 DATABASE_CONNECTION
        import src.database.data_access_object as dao_module
        dao_module.DATABASE_CONNECTION = db_conn
        
        print("\n--- 步骤1: 初始化引擎并执行全量同步 ---")
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        stats = engine.full_sync()
        
        print(f"\n全量同步结果:")
        print(f"  文件处理: {stats.files_processed}")
        print(f"  类型处理: {stats.types_processed}")
        print(f"  函数处理: {stats.functions_processed}")
        
        # 检查一致性
        print("\n--- 步骤2: 检查全量同步后的一致性 ---")
        check_consistency(engine, "全量同步后")
        
        # 修改文件
        print("\n--- 步骤3: 修改文件并执行增量更新 ---")
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1
    def method2(self):
        return 3

def function1():
    return 2
def function2():
    return 4
""")
        
        update_stats = engine.process_events([test_file])
        print(f"\n增量更新结果:")
        print(f"  文件处理: {update_stats.files_processed}")
        print(f"  类型处理: {update_stats.types_processed}")
        print(f"  函数处理: {update_stats.functions_processed}")
        
        print("\n--- 步骤4: 检查增量更新后的一致性 ---")
        check_consistency(engine, "增量更新后")
        
        # 再次修改文件（删除内容）
        print("\n--- 步骤5: 再次修改文件（减少内容）---")
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1

def function1():
    return 2
""")
        
        update_stats2 = engine.process_events([test_file])
        print(f"\n第二次增量更新结果:")
        print(f"  文件处理: {update_stats2.files_processed}")
        print(f"  类型处理: {update_stats2.types_processed}")
        print(f"  函数处理: {update_stats2.functions_processed}")
        
        print("\n--- 步骤6: 检查第二次更新后的一致性 ---")
        check_consistency(engine, "第二次更新后")
        
        # 恢复原始数据库连接
        src.database.DATABASE_CONNECTION = original_db
        dao_module.DATABASE_CONNECTION = original_db
        
        print("\n" + "=" * 80)
        print("测试完成")
        print("=" * 80)


def check_consistency(engine, stage_name):
    """详细检查缓存与数据库的一致性"""
    print(f"\n【{stage_name}】")
    print("-" * 60)
    
    # 获取数据库数据
    db_files = FileDAO.get_all()
    db_types = TypeDAO.get_all()
    db_functions = FunctionDAO.get_all()
    
    # 缓存数据
    cache_files = len(engine._file_id_cache)
    cache_types = len(engine._type_cache)
    cache_functions = len(engine._function_cache)
    
    print(f"数据库统计:")
    print(f"  文件: {len(db_files)}")
    print(f"  类型: {len(db_types)}")
    print(f"  函数: {len(db_functions)}")
    
    print(f"\n内存缓存统计:")
    print(f"  文件缓存: {cache_files}")
    print(f"  类型缓存: {cache_types}")
    print(f"  函数缓存: {cache_functions}")
    
    # 检查具体数据
    print(f"\n类型数据对比:")
    print("  数据库中的类型:")
    for t in db_types[:10]:
        db_key = f"{t['name']}:{t['file_id']}"
        cache_val = engine._type_cache.get(db_key)
        status = "✓" if cache_val else "✗ 缺失"
        print(f"    {db_key} -> {status}")
    if len(db_types) > 10:
        print(f"    ... 还有 {len(db_types) - 10} 个")
    
    print(f"\n函数数据对比 (前10个):")
    print("  数据库中的函数:")
    for f in db_functions[:10]:
        db_key = f"{f['name']}:{f['type_id']}:{f['file_id']}"
        cache_val = engine._function_cache.get(db_key)
        status = "✓" if cache_val else "✗ 缺失"
        print(f"    {db_key} -> {status}")
    if len(db_functions) > 10:
        print(f"    ... 还有 {len(db_functions) - 10} 个")
    
    # 检查缓存中有但数据库没有的
    print(f"\n检查孤儿缓存项:")
    print(f"  类型缓存中的孤立项: {count_orphan_types(engine, db_types)}")
    print(f"  函数缓存中的孤立项: {count_orphan_functions(engine, db_functions)}")
    
    # 最终一致性结论
    types_ok = len(engine._type_cache) == len(db_types)
    functions_ok = len(engine._function_cache) == len(db_functions)
    
    print(f"\n【一致性结论】")
    print(f"  类型一致: {'✓ PASS' if types_ok else '✗ FAIL'}")
    print(f"  函数一致: {'✓ PASS' if functions_ok else '✗ FAIL'}")
    
    return types_ok and functions_ok


def count_orphan_types(engine, db_types):
    """计算孤儿类型缓存项"""
    db_type_keys = {f"{t['name']}:{t['file_id']}" for t in db_types}
    orphan = [k for k in engine._type_cache if k not in db_type_keys]
    if orphan:
        print(f"    孤儿类型键: {orphan[:5]}{'...' if len(orphan) > 5 else ''}")
    return len(orphan)


def count_orphan_functions(engine, db_functions):
    """计算孤儿函数缓存项"""
    db_func_keys = {f"{f['name']}:{f['type_id']}:{f['file_id']}" for f in db_functions}
    orphan = [k for k in engine._function_cache if k not in db_func_keys]
    if orphan:
        print(f"    孤儿函数键: {orphan[:5]}{'...' if len(orphan) > 5 else ''}")
    return len(orphan)


if __name__ == "__main__":
    isolated_cache_test()
