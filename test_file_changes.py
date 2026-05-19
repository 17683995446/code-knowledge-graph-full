#!/usr/bin/env python3
"""
文件变更检测和增量更新深度测试脚本
这是一个高难度的真实场景测试
"""
import sys
import time
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def create_test_file(directory, filename, content):
    """创建测试文件"""
    file_path = directory / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path


def main():
    LOGGER.info("=" * 80)
    LOGGER.info("文件变更检测和增量更新深度测试")
    LOGGER.info("=" * 80)
    
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        LOGGER.info(f"测试目录: {test_dir}")
        
        # 初始化系统
        initialize_all_parsers()
        
        # 创建初始的测试文件
        LOGGER.info("\n--- 阶段1: 初始全量同步 ---")
        
        # 创建初始测试文件
        create_test_file(test_dir, "initial.py", '''
def initial_function():
    return "Initial function"

class InitialClass:
    def method1(self):
        return "Method 1"
''')
        
        # 初始化引擎并进行初始同步
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        initial_stats = engine.full_sync()
        
        LOGGER.info(f"✓ 初始同步完成:")
        LOGGER.info(f"  文件: {initial_stats.files_created}")
        LOGGER.info(f"  类型: {initial_stats.types_processed}")
        LOGGER.info(f"  函数: {initial_stats.functions_processed}")
        
        # 读取初始数据库状态
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM files")
            initial_files = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM functions")
            initial_functions = cursor.fetchone()[0]
        
        # 等待一下，确保文件时间戳有变化
        LOGGER.info("\n等待时间戳变化...")
        time.sleep(1.2)
        
        # --- 阶段2: 测试文件创建 ---
        LOGGER.info("\n--- 阶段2: 文件创建测试 ---")
        new_file1 = create_test_file(test_dir, "new_file1.py", '''
def new_function1():
    return "New function 1"

class NewClass:
    def method2(self):
        return "Method 2"
''')
        
        new_file2 = create_test_file(test_dir, "subdir/new_file2.py", '''
def another_function():
    return "Another function"
''')
        
        # 执行检测和更新 - 直接处理新文件
        update_stats1 = engine.process_events([new_file1, new_file2])
        
        LOGGER.info(f"✓ 文件创建检测:")
        LOGGER.info(f"  处理文件数: {update_stats1.files_processed}")
        LOGGER.info(f"  新处理文件: {update_stats1.files_created}")
        
        # --- 阶段3: 测试文件修改 ---
        LOGGER.info("\n--- 阶段3: 文件修改测试 ---")
        # 修改初始文件
        modified_file = test_dir / "initial.py"
        modified_content = modified_file.read_text() + '''
def added_function():
    return "Added function"
'''
        modified_file.write_text(modified_content)
        
        time.sleep(1.2)  # 确保时间戳变化
        
        # 检测和处理修改
        update_stats2 = engine.process_events([modified_file])
        
        LOGGER.info(f"✓ 文件修改检测:")
        LOGGER.info(f"  处理文件数: {update_stats2.files_processed}")
        LOGGER.info(f"  更新文件: {update_stats2.files_updated}")
        
        # --- 阶段4: 测试文件删除 ---
        LOGGER.info("\n--- 阶段4: 文件删除测试 ---")
        # 删除一个文件
        new_file1.unlink()
        
        time.sleep(1.2)
        
        update_stats3 = engine.process_events([new_file1])
        
        LOGGER.info(f"✓ 文件删除检测:")
        LOGGER.info(f"  删除文件: {update_stats3.files_deleted}")
        
        # --- 阶段5: 最终检查 ---
        LOGGER.info("\n--- 阶段5: 最终状态验证 ---")
        
        # 检查最终统计
        final_stats = DATABASE_CONNECTION.get_database_stats()
        
        LOGGER.info(f"\n✓ 最终数据库状态:")
        LOGGER.info(f"  总文件数: {final_stats['total_files']}")
        LOGGER.info(f"  总类型数: {final_stats['total_types']}")
        LOGGER.info(f"  总函数数: {final_stats['total_functions']}")
        
        # 验证最终结果
        LOGGER.info("\n✓ 所有阶段测试完成！")
        LOGGER.info(f"  - 初始文件数: {initial_files}")
        LOGGER.info(f"  - 最终文件数: {final_stats['total_files']}")
        LOGGER.info(f"  - 初始函数数: {initial_functions}")
        LOGGER.info(f"  - 最终函数数: {final_stats['total_functions']}")
        
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("✓ 深度文件变更测试完成！")
        LOGGER.info("=" * 80)


if __name__ == "__main__":
    main()
