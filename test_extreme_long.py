#!/usr/bin/env python3
"""
超极限长时间压力测试 - 基于第一性原理
真实模拟频繁文件修改、多个文件同时更新
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


def create_initial_files(base_path: Path, num_files: int = 15):
    """创建初始的复杂文件集"""
    files = []
    
    for i in range(num_files):
        lang = random.choice(['py', 'js', 'go'])
        
        if lang == 'py':
            file_path = base_path / f"module_{i}.py"
            content = f"""
class ModuleClass{i}:
    def method1(self):
        return {i}
    
    def method2(self):
        return "test{i}"

def module_function{i}(x):
    return x + {i}
"""
        elif lang == 'js':
            file_path = base_path / f"component_{i}.jsx"
            content = f"""
export class Component{i} {{
    render() {{
        return <div>Component {{ {i} }}</div>;
    }}
    
    handleClick() {{
        console.log({i});
    }}
}}

export function helper{i}(data) {{
    return data + {i};
}}
"""
        else:  # go
            file_path = base_path / f"service_{i}.go"
            content = f"""
package main

type Service{i} struct {{
    Count int
}}

func (s *Service{i}) Increment() {{
    s.Count++
}}

func (s *Service{i}) Get() int {{
    return s.Count
}}
"""
        
        file_path.write_text(content)
        files.append(file_path)
    
    return files


def modify_file(file_path: Path, iteration: int):
    """修改文件内容"""
    content = file_path.read_text()
    suffix = file_path.suffix
    
    if suffix == '.py':
        added = f"""

# Iteration {iteration}
def dynamic_func{iteration}(x):
    return x + {iteration}
"""
    elif suffix == '.jsx':
        added = f"""

// Iteration {iteration}
export function dynamic{iteration}(value) {{
    return value + {iteration};
}}
"""
    else:
        added = f"""

// Iteration {iteration}
func Dynamic{iteration}(x int) int {{
    return x + {iteration}
}}
"""
    
    file_path.write_text(content + added)


def run_extreme_long_test():
    """超极限长时间测试"""
    LOGGER.info("=" * 80)
    LOGGER.info("🔥 超极限长时间压力测试")
    LOGGER.info("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir)
        
        # 创建初始文件
        LOGGER.info("\n1. 初始文件创建")
        files = create_initial_files(test_path, num_files=15)
        LOGGER.info(f"  创建了 {len(files)} 个混合语言的源文件")
        
        # 初始化系统
        engine = IncrementalUpdateEngine(test_path)
        engine.initialize()
        
        # 完整同步
        LOGGER.info("\n2. 完整初始同步")
        stats = engine.full_sync()
        
        db_stats1 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  初始数据库: {db_stats1['total_files']}文件, {db_stats1['total_types']}类型, {db_stats1['total_functions']}函数")
        
        # 长期迭代修改
        LOGGER.info("\n3. 开始极限长时间迭代修改")
        num_iterations = 25
        
        for iter_idx in range(num_iterations):
            LOGGER.info(f"\n  --- 迭代 {iter_idx + 1}/{num_iterations} ---")
            
            # 随机修改2-8个文件
            num_modify = random.randint(2, 8)
            files_to_modify = random.sample(files, min(num_modify, len(files)))
            
            for file_path in files_to_modify:
                modify_file(file_path, iter_idx)
            
            # 处理修改
            update_stats = engine.process_events(files_to_modify)
            
            # 检查一致性
            db_stats_now = DATABASE_CONNECTION.get_database_stats()
            cache_files = len(engine._file_id_cache)
            cache_types = len(engine._type_cache)
            cache_funcs = len(engine._function_cache)
            
            LOGGER.info(f"    修改了 {len(files_to_modify)} 个文件")
            LOGGER.info(f"    数据库: {db_stats_now['total_files']}文件, {db_stats_now['total_types']}类型, {db_stats_now['total_functions']}函数")
            LOGGER.info(f"    缓存: {cache_files}文件, {cache_types}类型, {cache_funcs}函数")
            
            # 验证一致性
            assert cache_files == db_stats_now['total_files'], f"文件缓存不一致：{cache_files} vs {db_stats_now['total_files']}"
            assert cache_types == db_stats_now['total_types'], f"类型缓存不一致：{cache_types} vs {db_stats_now['total_types']}"
            assert cache_funcs == db_stats_now['total_functions'], f"函数缓存不一致：{cache_funcs} vs {db_stats_now['total_functions']}"
            
            LOGGER.info("    ✓ 缓存与数据库完全一致！")
            
            # 偶尔添加新文件
            if iter_idx % 3 == 0:
                new_file = test_path / f"new_file_{iter_idx}.py"
                new_file.write_text(f"""
class NewClass{iter_idx}:
    def test(self):
        return "new {iter_idx}"

def new_func{iter_idx}():
    return "test {iter_idx}"
""")
                
                files.append(new_file)
                engine.process_events([new_file])
                LOGGER.info(f"    + 添加了新文件: {new_file.name}")
            
            # 偶尔删除文件
            if iter_idx % 5 == 0 and len(files) > 5:
                file_to_delete = random.choice(files)
                file_to_delete.unlink()
                files.remove(file_to_delete)
                engine.process_events([file_to_delete])
                LOGGER.info(f"    - 删除了文件: {file_to_delete.name}")
        
        # 最终验证
        LOGGER.info("\n" + "=" * 80)
        final_db = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info("✅ 极限测试完成！")
        LOGGER.info(f"  最终数据库状态:")
        LOGGER.info(f"    文件数: {final_db['total_files']}")
        LOGGER.info(f"    类型数: {final_db['total_types']}")
        LOGGER.info(f"    函数数: {final_db['total_functions']}")
        LOGGER.info(f"  缓存与数据库完全一致！")
        LOGGER.info(f"  系统在 {num_iterations} 轮迭代后完美稳定！")
        LOGGER.info("=" * 80)
        
        return True


if __name__ == "__main__":
    try:
        success = run_extreme_long_test()
        if success:
            LOGGER.info("\n🎉 恭喜！所有极限测试完美通过！")
        else:
            LOGGER.info("\n✗ 测试发现问题！")
    except Exception as e:
        LOGGER.error(f"\n✗ 测试发生异常: {e}")
        import traceback
        traceback.print_exc()
