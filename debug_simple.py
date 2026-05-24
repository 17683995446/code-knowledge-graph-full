#!/usr/bin/env python3
"""简单调试缓存不一致问题"""

import sys
import tempfile
import shutil
from pathlib import Path

# 确保我们从当前目录加载模块
sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_cache_issue():
    """调试核心问题"""
    
    print("=" * 60)
    print("开始调试缓存不一致问题")
    print("=" * 60)
    
    # 1. 初始化
    initialize_all_parsers()
    
    # 2. 创建临时工作目录（独立的）
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"\n使用临时目录: {temp_path}")
        
        # 3. 初始化数据库连接（使用临时目录的数据库）
        original_db_path = None
        if hasattr(DATABASE_CONNECTION, 'db_path'):
            original_db_path = DATABASE_CONNECTION.db_path
            DATABASE_CONNECTION.db_path = str(temp_path / 'test.db')
        
        # 清理可能的旧数据库
        if (temp_path / 'test.db').exists():
            (temp_path / 'test.db').unlink()
        
        # 4. 创建初始测试文件
        test_file = temp_path / "test_module.py"
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1

def function1():
    return 2
""")
        
        print(f"\n创建测试文件: {test_file}")
        
        # 5. 初始化引擎并全量同步
        print("\n--- 步骤1: 执行全量同步 ---")
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        stats = engine.full_sync()
        
        print(f"同步结果: {stats}")
        
        # 6. 检查缓存与数据库是否一致
        print("\n--- 步骤2: 检查缓存与数据库一致性 ---")
        check_consistency(engine, "初始同步后")
        
        # 7. 修改测试文件
        print("\n--- 步骤3: 修改文件并更新 ---")
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
        print(f"更新结果: {update_stats}")
        
        # 8. 再次检查一致性
        print("\n--- 步骤4: 更新后检查一致性 ---")
        check_consistency(engine, "文件更新后")
        
        print("\n" + "=" * 60)
        print("调试完成")
        print("=" * 60)


def check_consistency(engine, stage_name):
    """检查缓存与数据库一致性"""
    print(f"\n{stage_name}:")
    
    # 获取数据库中的所有数据
    db_files = FileDAO.get_all()
    db_types = TypeDAO.get_all()
    db_functions = FunctionDAO.get_all()
    
    print(f"  数据库:")
    print(f"    文件: {len(db_files)}")
    print(f"    类型: {len(db_types)}")
    for t in db_types:
        print(f"      - {t['name']} (file_id={t['file_id']})")
    print(f"    函数: {len(db_functions)}")
    for f in db_functions:
        print(f"      - {f['name']} (type_id={f['type_id']}, file_id={f['file_id']})")
    
    print(f"  缓存:")
    print(f"    文件缓存: {len(engine._file_id_cache)}")
    print(f"    类型缓存: {len(engine._type_cache)}")
    for key, t in engine._type_cache.items():
        print(f"      - {key} -> {t}")
    print(f"    函数缓存: {len(engine._function_cache)}")
    for key, f in engine._function_cache.items():
        print(f"      - {key} -> {f}")
    
    # 检查一致性
    types_ok = len(engine._type_cache) == len(db_types)
    functions_ok = len(engine._function_cache) == len(db_functions)
    
    print(f"\n  一致性检查:")
    print(f"    类型: {'✓ OK' if types_ok else '✗ FAILED'}")
    print(f"    函数: {'✓ OK' if functions_ok else '✗ FAILED'}")
    
    return types_ok and functions_ok


if __name__ == "__main__":
    debug_cache_issue()
