#!/usr/bin/env python3
"""
更简单的测试，定位第二个真实Bug
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def test_simple_multiple_file_update():
    """简单但明确的测试，定位第二个问题"""
    LOGGER.info("=" * 80)
    LOGGER.info("简单测试：多文件修改定位问题")
    LOGGER.info("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir)
        
        # 创建2个测试文件
        file1 = test_path / "file1.py"
        file1.write_text("""
class Class1:
    def method1(self):
        return 1

def func1():
    return "test"
""")
        
        file2 = test_path / "file2.py"
        file2.write_text("""
class Class2:
    def method2(self):
        return 2

def func2():
    return "test"
""")
        
        LOGGER.info("\n1. 初始同步")
        engine = IncrementalUpdateEngine(test_path)
        engine.initialize()
        
        stats1 = engine.full_sync()
        LOGGER.info(f"  同步: {stats1.files_processed}文件, {stats1.types_processed}类型, {stats1.functions_processed}函数")
        
        db1 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  数据库: {db1['total_files']}文件, {db1['total_types']}类型, {db1['total_functions']}函数")
        LOGGER.info(f"  缓存: {len(engine._file_id_cache)}文件, {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        # 同时修改两个文件
        LOGGER.info("\n2. 同时修改两个文件")
        file1.write_text("""
class NewClass1:
    def new_method1(self):
        return "new"

def new_func1():
    return "new"
""")
        
        file2.write_text("""
class NewClass2:
    def new_method2(self):
        return "new"

def new_func2():
    return "new"
""")
        
        # 处理修改
        LOGGER.info("\n3. 处理两个文件的修改")
        update_stats = engine.process_events([file1, file2])
        
        LOGGER.info(f"  更新统计: {update_stats.files_processed}文件, {update_stats.types_processed}类型, {update_stats.functions_processed}函数")
        
        db2 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"\n  现在数据库: {db2['total_files']}文件, {db2['total_types']}类型, {db2['total_functions']}函数")
        LOGGER.info(f"  现在缓存: {len(engine._file_id_cache)}文件, {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        LOGGER.info(f"\n  缓存类型键: {list(engine._type_cache.keys())}")
        LOGGER.info(f"  缓存函数键: {list(engine._function_cache.keys())}")
        
        # 详细检查缓存内容
        LOGGER.info(f"\n4. 详细分析缓存")
        for key, val in engine._type_cache.items():
            LOGGER.info(f"  Type Cache - {key}: file_id={val.get('file_id')}")
        for key, val in engine._function_cache.items():
            LOGGER.info(f"  Func Cache - {key}: file_id={val.get('file_id')}")
        
        # 检查一致性
        if len(engine._type_cache) == db2['total_types'] and len(engine._function_cache) == db2['total_functions']:
            LOGGER.info("\n✅ 缓存与数据库一致！")
            return True
        else:
            LOGGER.error("\n❌ 发现不一致！")
            LOGGER.error(f"   DB: {db2['total_types']}类型, {db2['total_functions']}函数")
            LOGGER.error(f"   Cache: {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
            return False


if __name__ == "__main__":
    result = test_simple_multiple_file_update()
    if result:
        LOGGER.info("\n🎉 测试通过！")
    else:
        LOGGER.info("\n❌ 发现问题！")
