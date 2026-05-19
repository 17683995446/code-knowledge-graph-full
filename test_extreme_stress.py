#!/usr/bin/env python3
"""
极端压力测试脚本
测试大规模代码变更、快速迭代和系统稳定性
"""
import sys
import time
import tempfile
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def create_massive_test_files(base_dir: Path, num_files: int = 100):
    """创建大量测试文件"""
    files = []
    
    for i in range(num_files):
        file_path = base_dir / f"test_module_{i}.py"
        
        content = f'''
"""测试模块 {i}"""

class Class{i}:
    """测试类"""
    
    def method1(self):
        return f"Class{i}.method1"
    
    def method2(self):
        return f"Class{i}.method2"


def function{i}(x: int) -> int:
    """测试函数"""
    return x + {i}


def main():
    """主函数"""
    obj = Class{i}()
    result = obj.method1()
    print(result)


if __name__ == "__main__":
    main()
'''
        file_path.write_text(content)
        files.append(file_path)
    
    return files


def main():
    LOGGER.info("=" * 80)
    LOGGER.info("极端压力测试 - 大规模代码变更")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        LOGGER.info(f"测试目录: {test_dir}")
        
        initialize_all_parsers()
        
        # 初始化引擎
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        # 阶段1: 初始创建大量文件
        LOGGER.info("\n--- 阶段1: 创建大量初始文件 ---")
        num_files = 50
        start = time.time()
        
        test_files = create_massive_test_files(test_dir, num_files)
        
        stats = engine.full_sync()
        
        elapsed = time.time() - start
        LOGGER.info(f"✓ 初始同步完成: {elapsed:.2f}秒")
        LOGGER.info(f"  文件数: {stats.files_processed}")
        LOGGER.info(f"  类型数: {stats.types_processed}")
        LOGGER.info(f"  函数数: {stats.functions_processed}")
        
        db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"✓ 数据库确认: 总文件 {db_stats['total_files']}，总类型 {db_stats['total_types']}，总函数 {db_stats['total_functions']}")
        
        # 阶段2: 快速迭代修改
        LOGGER.info("\n--- 阶段2: 快速迭代修改 ---")
        num_iterations = 20
        start = time.time()
        
        for iteration in range(num_iterations):
            # 随机选择一些文件进行修改
            num_changes = random.randint(5, 15)
            files_to_modify = random.sample(test_files, min(num_changes, len(test_files)))
            
            for file_path in files_to_modify:
                content = file_path.read_text()
                new_content = content + f'''
def added_in_iteration_{iteration}(x):
    return x * {iteration}
'''
                file_path.write_text(new_content)
            
            # 执行增量更新
            engine.process_events(files_to_modify)
            
            if (iteration + 1) % 5 == 0:
                LOGGER.info(f"  完成 {iteration + 1}/{num_iterations} 轮迭代")
        
        elapsed = time.time() - start
        LOGGER.info(f"✓ {num_iterations} 轮迭代修改完成: {elapsed:.2f}秒")
        LOGGER.info(f"  平均每轮: {elapsed/num_iterations:.3f}秒")
        
        # 阶段3: 批量删除
        LOGGER.info("\n--- 阶段3: 批量删除测试 ---")
        num_deletes = random.randint(10, 30)
        files_to_delete = random.sample(test_files, num_deletes)
        
        start = time.time()
        for file_path in files_to_delete:
            file_path.unlink()
            test_files.remove(file_path)
        
        engine.process_events(files_to_delete)
        
        elapsed = time.time() - start
        LOGGER.info(f"✓ 删除 {num_deletes} 个文件完成: {elapsed:.2f}秒")
        
        # 阶段4: 最终验证
        LOGGER.info("\n--- 阶段4: 最终验证 ---")
        final_db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"✓ 最终数据库状态:")
        LOGGER.info(f"  总文件数: {final_db_stats['total_files']}")
        LOGGER.info(f"  总类型数: {final_db_stats['total_types']}")
        LOGGER.info(f"  总函数数: {final_db_stats['total_functions']}")
        
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("✓ 极端压力测试完成 - 系统稳定运行！")
        LOGGER.info("=" * 80)


if __name__ == "__main__":
    main()
