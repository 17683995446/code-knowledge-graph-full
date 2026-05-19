#!/usr/bin/env python3
"""
基于第一性原理的深度测试
发现并验证真实Bug：缓存与数据库不一致问题
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def test_cache_inconsistency_bug():
    """测试缓存与数据库不一致的真实Bug"""
    LOGGER.info("=" * 80)
    LOGGER.info("测试真实Bug：缓存与数据库不一致问题")
    LOGGER.info("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir)
        
        # 创建测试文件
        test_file = test_path / "test_file.py"
        test_file.write_text("""
class TestClass:
    def test_method(self):
        return "test"

def test_function():
    return "function"
""")
        
        LOGGER.info("\n1. 初始同步")
        engine = IncrementalUpdateEngine(test_path)
        engine.initialize()
        
        stats1 = engine.full_sync()
        LOGGER.info(f"  初始同步: {stats1.files_processed}文件, {stats1.types_processed}类型, {stats1.functions_processed}函数")
        
        db_stats1 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  数据库: {db_stats1['total_files']}文件, {db_stats1['total_types']}类型, {db_stats1['total_functions']}函数")
        LOGGER.info(f"  内存缓存: {len(engine._file_id_cache)}文件, {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        # 检查一致
        assert len(engine._type_cache) == db_stats1['total_types'], "初始缓存与类型数应该一致!"
        assert len(engine._function_cache) == db_stats1['total_functions'], "初始缓存与函数数应该一致!"
        
        LOGGER.info("✓ 初始状态：缓存与数据库一致")
        
        # 修改文件
        LOGGER.info("\n2. 修改文件")
        test_file.write_text("""
class NewClass:
    def new_method(self):
        return "new"

def new_function():
    return "new"
""")
        
        # 处理文件更新
        update_stats = engine.process_events([test_file])
        LOGGER.info(f"  更新统计: {update_stats.files_processed}文件, {update_stats.types_processed}类型, {update_stats.functions_processed}函数")
        
        db_stats2 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  数据库现在: {db_stats2['total_files']}文件, {db_stats2['total_types']}类型, {db_stats2['total_functions']}函数")
        LOGGER.info(f"  内存缓存现在: {len(engine._file_id_cache)}文件, {len(engine._type_cache)}类型, {len(engine._function_cache)}函数")
        
        # 发现Bug：缓存类型/函数数量应该和数据库一致，但会多！
        if len(engine._type_cache) != db_stats2['total_types'] or len(engine._function_cache) != db_stats2['total_functions']:
            LOGGER.error("✗ 发现真实Bug！内存缓存没有正确清理！")
            LOGGER.error(f"  数据库类型: {db_stats2['total_types']}, 缓存类型: {len(engine._type_cache)}")
            LOGGER.error(f"  数据库函数: {db_stats2['total_functions']}, 缓存函数: {len(engine._function_cache)}")
            return False
        else:
            LOGGER.info("✓ 缓存与数据库一致！")
        
        return True


if __name__ == "__main__":
    try:
        result = test_cache_inconsistency_bug()
        if result:
            LOGGER.info("\n🎉 恭喜！Bug不存在或已修复！")
        else:
            LOGGER.info("\n✗ Bug已发现，需要修复！")
    except Exception as e:
        LOGGER.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
