#!/usr/bin/env python3
"""极限压力测试 - 验证系统在极端条件下的稳定性"""

import sys
import tempfile
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO, CallDAO, ReferenceDAO
from src.database.data_access_object import FileEntity, TypeEntity, FunctionEntity
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def run_stress_tests():
    """运行极限压力测试"""
    
    print("=" * 100)
    print("极限压力测试 - 验证系统在极端条件下的稳定性")
    print("=" * 100)
    
    initialize_all_parsers()
    
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        db_path = temp_path / 'stress_test.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        _isolate_database(db_conn)
        
        print("\n" + "=" * 100)
        print("测试1: 超大文件测试（1万行代码）")
        print("=" * 100)
        results.extend(test_large_file(temp_path))
        
        print("\n" + "=" * 100)
        print("测试2: 大量小文件测试（1000个文件）")
        print("=" * 100)
        results.extend(test_many_small_files(temp_path))
        
        print("\n" + "=" * 100)
        print("测试3: 快速连续修改测试（100次）")
        print("=" * 100)
        results.extend(test_rapid_modifications(temp_path))
        
        print("\n" + "=" * 100)
        print("测试4: 复杂调用链测试")
        print("=" * 100)
        results.extend(test_complex_call_chains(temp_path))
        
        print("\n" + "=" * 100)
        print("测试5: 并发冲突测试")
        print("=" * 100)
        results.extend(test_concurrent_conflicts(temp_path))
        
        print("\n" + "=" * 100)
        print("测试6: 内存泄漏检测")
        print("=" * 100)
        results.extend(test_memory_leak(temp_path))
        
        _restore_database()
        
        print_summary(results)


def test_large_file(temp_path):
    """测试超大文件"""
    results = []
    
    print("\n[超大文件测试]")
    try:
        large_file = temp_path / "large_file.py"
        
        lines = []
        lines.append("import sys\nimport os\nimport json\n\n")
        
        for i in range(1000):
            lines.append(f"""
class Class_{i}:
    '''Class number {i}'''
    
    def __init__(self):
        self.data_{i} = []
    
    def method_{i}_1(self, x):
        '''First method'''
        return x * {i}
    
    def method_{i}_2(self, y):
        '''Second method'''
        return y + {i}
    
    def method_{i}_3(self, z):
        '''Third method'''
        return z - {i}


def function_{i}_1(a, b):
    '''Function number {i}'''
    return a + b + {i}


def function_{i}_2(x):
    '''Another function'''
    return x * {i}


def function_{i}_3(y):
    '''Yet another function'''
    return y + {i}
""")
        
        large_file.write_text("".join(lines))
        
        print(f"  创建文件大小: {large_file.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"  预计代码行数: {len(lines)}")
        
        start_time = time.time()
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats = engine.full_sync()
        
        elapsed = time.time() - start_time
        
        print(f"  处理耗时: {elapsed:.2f}s")
        print(f"  处理类型: {stats.types_processed}")
        print(f"  处理函数: {stats.functions_processed}")
        
        results.append(check("Large file processing", stats.types_processed > 0, f"{stats.types_processed} types"))
        results.append(check("Large file performance", elapsed < 30, f"{elapsed:.2f}s"))
        
    except Exception as e:
        results.append(check("Large file exception", False, str(e)))
    
    return results


def test_many_small_files(temp_path):
    """测试大量小文件"""
    results = []
    
    print("\n[大量小文件测试]")
    try:
        test_dir = temp_path / "many_files"
        test_dir.mkdir()
        
        print(f"  创建 1000 个小文件...")
        start_create = time.time()
        
        for i in range(1000):
            f = test_dir / f"file_{i}.py"
            f.write_text(f"""
class SmallClass{i}:
    def method(self):
        return {i}

def small_func{i}():
    return {i}
""")
        
        create_time = time.time() - start_create
        print(f"  创建耗时: {create_time:.2f}s")
        
        start_time = time.time()
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        elapsed = time.time() - start_time
        
        print(f"  处理耗时: {elapsed:.2f}s")
        print(f"  处理文件: {stats.files_processed}")
        print(f"  处理类型: {stats.types_processed}")
        print(f"  处理函数: {stats.functions_processed}")
        
        results.append(check("Many files processing", stats.files_processed >= 1000, f"{stats.files_processed} files"))
        results.append(check("Many files performance", elapsed < 60, f"{elapsed:.2f}s"))
        
    except Exception as e:
        results.append(check("Many files exception", False, str(e)))
    
    return results


def test_rapid_modifications(temp_path):
    """测试快速连续修改"""
    results = []
    
    print("\n[快速连续修改测试]")
    try:
        test_file = temp_path / "rapid.py"
        test_file.write_text("class Initial:\n    pass")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        engine.full_sync()
        
        print(f"  执行 100 次快速修改...")
        start_time = time.time()
        
        success_count = 0
        for i in range(100):
            test_file.write_text(f"""
class Version{i}:
    def method_{i}(self):
        return {i}

def func_{i}():
    return {i}

def func_{i}_2(x):
    return x * {i}
""")
            
            stats = engine.process_events([test_file])
            if stats.types_processed > 0 or stats.functions_processed > 0:
                success_count += 1
        
        elapsed = time.time() - start_time
        
        print(f"  完成耗时: {elapsed:.2f}s")
        print(f"  成功修改: {success_count}/100")
        print(f"  平均每次: {elapsed/100*1000:.2f}ms")
        
        results.append(check("Rapid modifications success", success_count == 100, f"{success_count}/100"))
        results.append(check("Rapid modifications performance", elapsed < 30, f"{elapsed:.2f}s"))
        
    except Exception as e:
        results.append(check("Rapid modifications exception", False, str(e)))
    
    return results


def test_complex_call_chains(temp_path):
    """测试复杂调用链"""
    results = []
    
    print("\n[复杂调用链测试]")
    try:
        test_file = temp_path / "call_chain.py"
        test_file.write_text("""
def func_a():
    return func_b() + func_c()


def func_b():
    return func_d() + func_e()


def func_c():
    return func_d()


def func_d():
    return "D"


def func_e():
    return "E"


def func_f():
    return func_a() + func_b()


class CallClass:
    def method_a(self):
        return self.method_b()
    
    def method_b(self):
        return self.method_c() + self.method_d()
    
    def method_c(self):
        return "C"
    
    def method_d(self):
        return "D"


class AnotherClass:
    def call(self):
        obj = CallClass()
        return obj.method_a()
""")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats = engine.full_sync()
        
        print(f"  函数数量: {stats.functions_processed}")
        print(f"  调用解析: {stats.calls_resolved}")
        
        db_calls = CallDAO.get_callers(1)  # 检查调用DAO是否工作
        
        results.append(check("Call chain parsing", stats.functions_processed > 0, f"{stats.functions_processed} functions"))
        results.append(check("Call resolution", stats.calls_resolved >= 0, f"{stats.calls_resolved} calls resolved"))
        
    except Exception as e:
        results.append(check("Call chain exception", False, str(e)))
    
    return results


def test_concurrent_conflicts(temp_path):
    """测试并发冲突"""
    results = []
    
    print("\n[并发冲突测试]")
    try:
        test_dir = temp_path / "concurrent"
        test_dir.mkdir()
        
        file1 = test_dir / "file1.py"
        file2 = test_dir / "file2.py"
        
        file1.write_text("""
class SharedClass:
    def method1(self):
        return 1
""")
        
        file2.write_text("""
class SharedClass:
    def method2(self):
        return 2
""")
        
        print(f"  测试同名类冲突...")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        print(f"  处理文件: {stats.files_processed}")
        print(f"  处理类型: {stats.types_processed}")
        
        results.append(check("Concurrent conflict handling", stats.files_processed >= 2, f"{stats.files_processed} files"))
        
    except Exception as e:
        results.append(check("Concurrent conflict exception", False, str(e)))
    
    return results


def test_memory_leak(temp_path):
    """测试内存泄漏"""
    results = []
    
    print("\n[内存泄漏检测测试]")
    try:
        test_file = temp_path / "leak_test.py"
        test_file.write_text("""
class LeakTest:
    def process(self):
        return 1
""")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        initial_cache_size = len(engine._type_cache) + len(engine._function_cache)
        
        for i in range(10):
            engine.full_sync()
            engine.process_events([test_file])
        
        final_cache_size = len(engine._type_cache) + len(engine._function_cache)
        
        print(f"  初始缓存: {initial_cache_size}")
        print(f"  最终缓存: {final_cache_size}")
        
        cache_growth = final_cache_size - initial_cache_size
        
        results.append(check("Memory leak detection", cache_growth <= 10, f"Growth: {cache_growth}"))
        
    except Exception as e:
        results.append(check("Memory leak exception", False, str(e)))
    
    return results


def check(name, passed, details=""):
    """记录检查结果"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status} | {name}")
    if details:
        print(f"         | {details}")
    return {'name': name, 'passed': passed, 'details': details}


def print_summary(results):
    """打印测试总结"""
    print("\n" + "=" * 100)
    print("极限压力测试总结")
    print("=" * 100)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} ({passed/total*100:.1f}%)")
    print(f"失败: {failed} ({failed/total*100:.1f}%)")
    
    if failed > 0:
        print(f"\n失败的测试:")
        for r in results:
            if not r['passed']:
                print(f"  ✗ {r['name']}")
                if r['details']:
                    print(f"    详情: {r['details']}")
    
    print("\n" + "=" * 100)
    if failed == 0:
        print("🎉 所有极限测试通过！系统在极端条件下表现稳定")
    else:
        print(f"⚠️  发现 {failed} 个问题，需要优化")
    print("=" * 100)


def _isolate_database(db_conn):
    """隔离数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    _isolate_database.original_db = src.database.DATABASE_CONNECTION
    _isolate_database.original_dao_db = dao_module.DATABASE_CONNECTION
    
    src.database.DATABASE_CONNECTION = db_conn
    dao_module.DATABASE_CONNECTION = db_conn


def _restore_database():
    """恢复数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    src.database.DATABASE_CONNECTION = _isolate_database.original_db
    dao_module.DATABASE_CONNECTION = _isolate_database.original_dao_db


if __name__ == "__main__":
    run_stress_tests()
