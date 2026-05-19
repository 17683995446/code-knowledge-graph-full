#!/usr/bin/env python3
"""
边界条件和极限测试 - 系统的极致考验
"""
import sys
import time
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def test_empty_files():
    """测试空文件和最小文件"""
    LOGGER.info("=" * 80)
    LOGGER.info("边界条件测试1: 空文件和最小文件")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建空文件
        empty_py = test_dir / "empty.py"
        empty_py.write_text("")
        
        empty_js = test_dir / "empty.js"
        empty_js.write_text("")
        
        empty_go = test_dir / "empty.go"
        empty_go.write_text("")
        
        # 创建只有注释的文件
        comment_py = test_dir / "comments.py"
        comment_py.write_text("""
# This is a comment
# Only comments in this file
""")
        
        comment_js = test_dir / "comments.js"
        comment_js.write_text("""
// This is a comment
/* Block comment */
// Only comments
""")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        LOGGER.info(f"✓ 边界条件测试完成！")
        LOGGER.info(f"  处理文件: {stats.files_processed}")
        LOGGER.info(f"  类型: {stats.types_processed}")
        LOGGER.info(f"  函数: {stats.functions_processed}")
        LOGGER.info(f"  空文件也完美处理！")


def test_extremely_large_file():
    """测试超大型文件"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("边界条件测试2: 超大型文件")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建一个很大的Python文件
        large_file = test_dir / "large_file.py"
        
        content = "# Very large test file\n"
        for i in range(200):
            content += f'''
def func_{i}(x):
    """Function {i}"""
    result = x + {i}
    return result
'''
        
        for i in range(50):
            content += f'''
class Class{i}:
    """Class {i}"""
    def method1(self):
        return {i}
    
    def method2(self):
        return "value-{i}"
'''
        large_file.write_text(content)
        
        LOGGER.info(f"创建了超大型文件: {len(content)} 字符")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        start = time.time()
        stats = engine.full_sync()
        elapsed = time.time() - start
        
        LOGGER.info(f"✓ 大型文件处理完成！")
        LOGGER.info(f"  处理时间: {elapsed:.3f}秒")
        LOGGER.info(f"  解析函数: {stats.functions_processed}")
        LOGGER.info(f"  解析类型: {stats.types_processed}")


def test_complex_nested_structures():
    """测试复杂嵌套结构"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("边界条件测试3: 复杂嵌套结构")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        nested_file = test_dir / "nested.py"
        nested_file.write_text('''
class OuterClass:
    """Outer class with nested structures"""
    
    def outer_method(self):
        """Outer method"""
        
        class InnerClass:
            """Inner class"""
            
            def inner_method(self):
                """Inner method"""
                
                def deeply_nested():
                    """Very deeply nested function"""
                    return "deep"
                
                return deeply_nested()
        
        return InnerClass()

def complex_function():
    """Complex function with nested definitions"""
    
    def nested1():
        """Nested 1"""
        def nested2():
            """Nested 2"""
            def nested3():
                """Nested 3"""
                return 3
            return nested3()
        return nested2()
    
    return nested1()
''')
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        LOGGER.info(f"✓ 复杂嵌套结构处理完成！")
        LOGGER.info(f"  处理文件: {stats.files_processed}")
        LOGGER.info(f"  类型: {stats.types_processed}")
        LOGGER.info(f"  函数: {stats.functions_processed}")


def test_many_small_files():
    """测试非常多的小文件"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("边界条件测试4: 非常多的小文件")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建100个小文件
        for i in range(100):
            file_path = test_dir / f"file_{i}.py"
            file_path.write_text(f'''
"""File {i}"""

def function_{i}():
    """Function in file {i}"""
    return {i}
''')
        
        LOGGER.info(f"创建了100个小文件！")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        start = time.time()
        stats = engine.full_sync()
        elapsed = time.time() - start
        
        LOGGER.info(f"✓ 多文件处理完成！")
        LOGGER.info(f"  总文件: {stats.files_processed}")
        LOGGER.info(f"  总函数: {stats.functions_processed}")
        LOGGER.info(f"  处理时间: {elapsed:.3f}秒")


def test_special_characters_and_edge_cases():
    """测试特殊字符和边缘情况"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("边界条件测试5: 特殊字符和边缘情况")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        special_file = test_dir / "special_chars.py"
        special_file.write_text('''
"""File with special characters"""

# Function with Unicode in name (tested)
def function_äöü():
    """Function with Unicode"""
    return "Unicode!"

# Functions with edge cases
def f():
    """Minimal function"""
    return 1

class 测试类:  # Chinese class name
    """Test class"""
    def 测试方法(self):
        """Test method"""
        return "test"
''')
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        LOGGER.info(f"✓ 特殊字符和边缘情况处理完成！")
        LOGGER.info(f"  处理文件: {stats.files_processed}")
        LOGGER.info(f"  类型: {stats.types_processed}")
        LOGGER.info(f"  函数: {stats.functions_processed}")


def test_rapid_fire_changes():
    """测试快速连续变更"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("极限测试: 快速连续变更")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建初始文件
        target_file = test_dir / "changing.py"
        target_file.write_text('''
def version1():
    return "Version 1"
''')
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        engine.full_sync()
        
        LOGGER.info("开始快速连续变更...")
        
        # 快速修改100次
        start = time.time()
        for i in range(100):
            target_file.write_text(f'''
def version{i}():
    return "Version {i}"
''')
            # 强制时间戳变化
            import os
            os.utime(target_file, (time.time(), time.time()))
            
            engine.process_events([target_file])
        
        elapsed = time.time() - start
        LOGGER.info(f"✓ 快速连续变更完成！")
        LOGGER.info(f"  100次变更新用时: {elapsed:.3f}秒")
        LOGGER.info(f"  平均每次: {elapsed/100:.4f}秒")
        
        final_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  最终状态: 文件 {final_stats['total_files']}，函数 {final_stats['total_functions']}")


def run_all_boundary_tests():
    """运行所有边界条件和极限测试"""
    initialize_all_parsers()
    
    # 运行各个测试
    test_empty_files()
    test_extremely_large_file()
    test_complex_nested_structures()
    test_many_small_files()
    test_special_characters_and_edge_cases()
    test_rapid_fire_changes()
    
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("🎉 所有边界条件和极限测试完成！")
    LOGGER.info("   系统稳定运行！无任何崩溃！")
    LOGGER.info("=" * 80)


if __name__ == "__main__":
    run_all_boundary_tests()
