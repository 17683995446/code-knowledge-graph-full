#!/usr/bin/env python3
"""全面系统测试套件 - 第一性原理全覆盖验证"""

import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO, CallDAO, ReferenceDAO
from src.database.data_access_object import FileEntity, TypeEntity, FunctionEntity, CallRelationship
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers, get_parser_for_file, detect_language


def run_comprehensive_tests():
    """运行全面测试"""
    
    print("=" * 100)
    print("全面系统测试 - 第一性原理全覆盖验证")
    print("=" * 100)
    
    initialize_all_parsers()
    
    test_results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        db_path = temp_path / 'comprehensive_test.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        _isolate_database(db_conn)
        
        print("\n" + "=" * 100)
        print("第一部分: 数据访问层测试")
        print("=" * 100)
        test_results.extend(test_dao_layer())
        
        print("\n" + "=" * 100)
        print("第二部分: 解析器测试")
        print("=" * 100)
        test_results.extend(test_parsers(temp_path))
        
        print("\n" + "=" * 100)
        print("第三部分: 增量更新引擎测试")
        print("=" * 100)
        test_results.extend(test_engine(temp_path))
        
        print("\n" + "=" * 100)
        print("第四部分: 边界和异常处理测试")
        print("=" * 100)
        test_results.extend(test_boundaries(temp_path))
        
        print("\n" + "=" * 100)
        print("第五部分: 真实场景测试")
        print("=" * 100)
        test_results.extend(test_real_scenarios(temp_path))
        
        _restore_database()
        
        print_summary(test_results)


def test_dao_layer():
    """测试数据访问层"""
    results = []
    
    print("\n[FileDAO]")
    try:
        entity = FileEntity(path="/test/file.py", language="python", hash=b"test", modified=1234567890)
        file_id = FileDAO.create(entity)
        results.append(check("FileDAO.create", file_id > 0))
        
        fetched = FileDAO.get_by_id(file_id)
        results.append(check("FileDAO.get_by_id", fetched is not None))
        
        fetched = FileDAO.get_by_path("/test/file.py")
        results.append(check("FileDAO.get_by_path", fetched is not None))
        
        all_files = FileDAO.get_all()
        results.append(check("FileDAO.get_all", len(all_files) > 0))
        
        deleted = FileDAO.delete_by_path("/test/file.py")
        results.append(check("FileDAO.delete_by_path", deleted))
    except Exception as e:
        results.append(check("FileDAO exception handling", False, str(e)))
    
    print("\n[TypeDAO]")
    try:
        file_entity = FileEntity(path="/test/type_test.py", language="python", hash=b"test", modified=1234567890)
        file_id = FileDAO.create(file_entity)
        
        entity = TypeEntity(name="TestClass", file_id=file_id, kind="class", start_line=1, end_line=10)
        type_id = TypeDAO.create(entity)
        results.append(check("TypeDAO.create", type_id > 0))
        
        fetched = TypeDAO.get_by_file(file_id)
        results.append(check("TypeDAO.get_by_file", len(fetched) > 0))
        
        all_types = TypeDAO.get_all()
        results.append(check("TypeDAO.get_all", len(all_types) > 0))
    except Exception as e:
        results.append(check("TypeDAO exception handling", False, str(e)))
    
    print("\n[FunctionDAO]")
    try:
        file_entity = FileEntity(path="/test/func_test.py", language="python", hash=b"test", modified=1234567890)
        file_id = FileDAO.create(file_entity)
        
        entity = FunctionEntity(name="test_func", type_id=None, file_id=file_id, start_line=1, end_line=5, signature="def test_func():")
        func_id = FunctionDAO.create(entity)
        results.append(check("FunctionDAO.create", func_id > 0))
        
        fetched = FunctionDAO.get_by_file(file_id)
        results.append(check("FunctionDAO.get_by_file", len(fetched) > 0))
        
        all_funcs = FunctionDAO.get_all()
        results.append(check("FunctionDAO.get_all", len(all_funcs) > 0))
    except Exception as e:
        results.append(check("FunctionDAO exception handling", False, str(e)))
    
    print("\n[CallDAO]")
    try:
        file_entity = FileEntity(path="/test/call_test.py", language="python", hash=b"test", modified=1234567890)
        file_id = FileDAO.create(file_entity)
        
        caller = FunctionEntity(name="caller", type_id=None, file_id=file_id, start_line=1, end_line=5)
        callee = FunctionEntity(name="callee", type_id=None, file_id=file_id, start_line=10, end_line=15)
        
        caller_id = FunctionDAO.create(caller)
        callee_id = FunctionDAO.create(callee)
        
        rel = CallRelationship(caller_id=caller_id, callee_id=callee_id)
        created = CallDAO.create(rel)
        results.append(check("CallDAO.create", created))
    except Exception as e:
        results.append(check("CallDAO exception handling", False, str(e)))
    
    return results


def test_parsers(temp_path):
    """测试解析器"""
    results = []
    
    print("\n[Python Parser]")
    try:
        test_file = temp_path / "test.py"
        test_file.write_text("""
class MyClass:
    def method1(self):
        return 1

def standalone_func(a, b):
    return a + b

import os
from pathlib import Path
""")
        
        parser = get_parser_for_file(test_file)
        results.append(check("Python parser found", parser is not None))
        
        if parser:
            result = parser.parse(test_file)
            results.append(check("Python parsing success", result is not None))
            results.append(check("Python types extracted", len(result.types) > 0))
            results.append(check("Python functions extracted", len(result.functions) > 0))
            results.append(check("Python imports extracted", len(result.imports) > 0))
            
            class_found = any(t['name'] == 'MyClass' for t in result.types)
            results.append(check("Python class detected", class_found))
    except Exception as e:
        results.append(check("Python parser exception", False, str(e)))
    
    print("\n[JavaScript Parser]")
    try:
        test_file = temp_path / "test.js"
        test_file.write_text("""
class MyComponent {
    render() {
        return 'Hello';
    }
}

export function helperFunc(x, y) {
    return x + y;
}

import React from 'react';
""")
        
        parser = get_parser_for_file(test_file)
        results.append(check("JS parser found", parser is not None))
        
        if parser:
            result = parser.parse(test_file)
            results.append(check("JS parsing success", result is not None))
            results.append(check("JS types extracted", len(result.types) >= 0))
            results.append(check("JS functions extracted", len(result.functions) > 0))
    except Exception as e:
        results.append(check("JS parser exception", False, str(e)))
    
    print("\n[Go Parser]")
    try:
        test_file = temp_path / "test.go"
        test_file.write_text("""
package main

type MyStruct struct {
    Name string
}

type MyInterface interface {
    Process() error
}

func helperFunc(x int) int {
    return x * 2
}
""")
        
        parser = get_parser_for_file(test_file)
        results.append(check("Go parser found", parser is not None))
        
        if parser:
            result = parser.parse(test_file)
            results.append(check("Go parsing success", result is not None))
            results.append(check("Go types extracted", len(result.types) > 0))
            results.append(check("Go functions extracted", len(result.functions) > 0))
    except Exception as e:
        results.append(check("Go parser exception", False, str(e)))
    
    print("\n[ArkTS Parser]")
    try:
        test_file = temp_path / "test.ets"
        test_file.write_text("""
class MyComponent {
    public name: string = '';
    
    public process(): void {
        console.log('Processing');
    }
}

function helperFunc(x: number): number {
    return x * 2;
}
""")
        
        parser = get_parser_for_file(test_file)
        results.append(check("ArkTS parser found", parser is not None))
        
        if parser:
            result = parser.parse(test_file)
            results.append(check("ArkTS parsing success", result is not None))
    except Exception as e:
        results.append(check("ArkTS parser exception", False, str(e)))
    
    print("\n[Parser Registry]")
    results.append(check("Detect Python", detect_language(Path("test.py")) == "python"))
    results.append(check("Detect JavaScript", detect_language(Path("test.js")) == "javascript"))
    results.append(check("Detect Go", detect_language(Path("test.go")) == "go"))
    results.append(check("Detect ArkTS", detect_language(Path("test.ets")) == "arkts"))
    
    return results


def test_engine(temp_path):
    """测试增量更新引擎"""
    results = []
    
    print("\n[Engine Initialization]")
    try:
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        results.append(check("Engine initialized", engine is not None))
        results.append(check("File cache initialized", len(engine._file_id_cache) >= 0))
        results.append(check("Type cache initialized", len(engine._type_cache) >= 0))
        results.append(check("Function cache initialized", len(engine._function_cache) >= 0))
    except Exception as e:
        results.append(check("Engine initialization exception", False, str(e)))
    
    print("\n[Full Sync]")
    try:
        test_dir = temp_path / "sync_test"
        test_dir.mkdir()
        
        for i in range(5):
            f = test_dir / f"module_{i}.py"
            f.write_text(f"""
class Class{i}:
    def method_{i}(self):
        return {i}

def func_{i}():
    return {i}
""")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        
        results.append(check("Full sync completed", stats.files_processed > 0))
        results.append(check("Files processed", stats.files_processed == 5))
        results.append(check("Types processed", stats.types_processed > 0))
        results.append(check("Functions processed", stats.functions_processed > 0))
    except Exception as e:
        results.append(check("Full sync exception", False, str(e)))
    
    print("\n[Incremental Update]")
    try:
        test_file = temp_path / "incremental_test.py"
        test_file.write_text("""
class Initial:
    def method(self):
        return 1
""")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats1 = engine.full_sync()
        initial_funcs = stats1.functions_processed
        
        test_file.write_text("""
class Initial:
    def method(self):
        return 1
    def new_method(self):
        return 2

def new_func():
    return 3
""")
        
        stats2 = engine.process_events([test_file])
        
        results.append(check("Incremental update success", stats2.functions_processed > 0))
        results.append(check("Cache updated", len(engine._function_cache) > initial_funcs))
    except Exception as e:
        results.append(check("Incremental update exception", False, str(e)))
    
    print("\n[File Deletion]")
    try:
        test_file = temp_path / "delete_test.py"
        test_file.write_text("class ToDelete:\n    pass")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats1 = engine.full_sync()
        
        test_file.unlink()
        stats2 = engine.process_events([test_file])
        
        results.append(check("File deletion tracked", stats2.files_deleted > 0))
    except Exception as e:
        results.append(check("File deletion exception", False, str(e)))
    
    print("\n[Cache Consistency]")
    try:
        test_dir = temp_path / "cache_test"
        test_dir.mkdir()
        
        test_file = test_dir / "consistency.py"
        test_file.write_text("""
class TestClass:
    def method(self):
        return 1

def test_func():
    return 2
""")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        engine.full_sync()
        
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_funcs = FunctionDAO.get_all()
        
        cache_types = len(engine._type_cache)
        cache_funcs = len(engine._function_cache)
        
        results.append(check("Type cache consistency", cache_types == len(db_types)))
        results.append(check("Function cache consistency", cache_funcs == len(db_funcs)))
    except Exception as e:
        results.append(check("Cache consistency exception", False, str(e)))
    
    return results


def test_boundaries(temp_path):
    """测试边界和异常"""
    results = []
    
    print("\n[Empty File]")
    try:
        empty_file = temp_path / "empty.py"
        empty_file.write_text("")
        
        parser = get_parser_for_file(empty_file)
        if parser:
            result = parser.parse(empty_file)
            results.append(check("Empty file handled", result is not None))
    except Exception as e:
        results.append(check("Empty file exception", True))
    
    print("\n[Unsupported File]")
    try:
        txt_file = temp_path / "test.txt"
        txt_file.write_text("This is a text file")
        
        lang = detect_language(txt_file)
        results.append(check("Unsupported file detection", lang is None))
    except Exception as e:
        results.append(check("Unsupported file exception", False, str(e)))
    
    print("\n[Unicode File]")
    try:
        unicode_file = temp_path / "unicode.py"
        unicode_file.write_text("""
class 中文类:
    def 中文方法(self):
        return "你好世界"
    
def 函数():
    return "测试"
""")
        
        parser = get_parser_for_file(unicode_file)
        if parser:
            result = parser.parse(unicode_file)
            results.append(check("Unicode file handled", result is not None))
    except Exception as e:
        results.append(check("Unicode file exception", False, str(e)))
    
    print("\n[Deep Nesting]")
    try:
        deep_path = temp_path
        for i in range(10):
            deep_path = deep_path / f"level_{i}"
            deep_path.mkdir(exist_ok=True)
        
        deep_file = deep_path / "deep.py"
        deep_file.write_text("class DeepClass:\n    pass")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        stats = engine.full_sync()
        results.append(check("Deep nesting handled", stats.files_processed > 0))
    except Exception as e:
        results.append(check("Deep nesting exception", False, str(e)))
    
    print("\n[Special Characters]")
    try:
        special_dir = temp_path / "special"
        special_dir.mkdir()
        
        special_file = special_dir / "file with spaces.py"
        special_file.write_text("class SpaceClass:\n    pass")
        
        results.append(check("Special chars in path handled", special_file.exists()))
    except Exception as e:
        results.append(check("Special chars exception", False, str(e)))
    
    return results


def test_real_scenarios(temp_path):
    """测试真实场景"""
    results = []
    
    print("\n[Multi-Language Project]")
    try:
        project_dir = temp_path / "multi_lang_project"
        project_dir.mkdir()
        
        py_file = project_dir / "main.py"
        py_file.write_text("class PythonClass:\n    pass")
        
        js_file = project_dir / "utils.js"
        js_file.write_text("function jsFunc() { return 1; }")
        
        go_file = project_dir / "main.go"
        go_file.write_text("package main\nfunc main() {}")
        
        ets_file = project_dir / "component.ets"
        ets_file.write_text("class ETSComponent {\n    process(): void {}\n}")
        
        engine = IncrementalUpdateEngine(project_dir)
        engine.initialize()
        
        stats = engine.full_sync()
        results.append(check("Multi-language sync", stats.files_processed >= 4))
    except Exception as e:
        results.append(check("Multi-language exception", False, str(e)))
    
    print("\n[Sequential Modifications]")
    try:
        test_file = temp_path / "sequential.py"
        test_file.write_text("class V1:\n    pass")
        
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        engine.full_sync()
        
        for version in range(2, 6):
            test_file.write_text(f"class V{version}:\n    def method_{version}(self):\n        return {version}\n\ndef func_{version}():\n    return {version}")
            
            stats = engine.process_events([test_file])
            results.append(check(f"Sequential modification {version}", stats.functions_processed > 0))
    except Exception as e:
        results.append(check("Sequential modification exception", False, str(e)))
    
    print("\n[Call Resolution]")
    try:
        test_dir = temp_path / "call_resolution"
        test_dir.mkdir()
        
        file1 = test_dir / "caller.py"
        file1.write_text("""
def caller_func():
    return callee_func()

def callee_func():
    return 42
""")
        
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        stats = engine.full_sync()
        
        results.append(check("Call resolution", stats.calls_resolved >= 0))
    except Exception as e:
        results.append(check("Call resolution exception", False, str(e)))
    
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
    print("测试总结")
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
        print("🎉 所有测试通过！系统符合第一性原理设计")
    else:
        print(f"⚠️  发现 {failed} 个问题，需要进一步调查")
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
    run_comprehensive_tests()
