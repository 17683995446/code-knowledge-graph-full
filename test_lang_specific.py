#!/usr/bin/env python3
"""测试特定语言的解析和增量更新"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def test_language_specific():
    """测试特定语言的解析"""
    
    print("=" * 80)
    print("测试特定语言的解析和增量更新")
    print("=" * 80)
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 创建独立的数据库
        db_path = temp_path / 'test.db'
        db_conn = DatabaseConnection(db_path)
        db_conn.initialize_database()
        
        # 隔离全局数据库连接
        _isolate_database(db_conn)
        
        # 创建不同语言的文件
        languages = {
            'python': ('.py', """
class TestClass:
    def method(self):
        return 1

def test_func():
    return 2
"""),
            'javascript': ('.js', """
function testFunc(x, y) {
    return x + y;
}

class TestClass {
    method() {
        return 1;
    }
}
"""),
            'jsx': ('.jsx', """
import React from 'react';

export class TestComponent {
    render() {
        return <div>Test</div>;
    }
}

export function helperFunc(x, y) {
    return x + y;
}
"""),
            'go': ('.go', """
package main

type TestStruct struct {
    Data string
}

func (c *TestStruct) Process() {
    return;
}

func helperFunc() {
    return;
}
"""),
        }
        
        files_created = []
        for lang, (ext, content) in languages.items():
            file = temp_path / f"{lang}_test{ext}"
            file.write_text(content)
            files_created.append(file)
            print(f"创建 {lang} 文件: {file}")
        
        # 初始化引擎
        engine = IncrementalUpdateEngine(temp_path)
        engine.initialize()
        
        # 同步
        print("\n--- 全量同步 ---")
        stats = engine.full_sync()
        print(f"结果: {stats.files_processed}文件, {stats.types_processed}类型, {stats.functions_processed}函数")
        
        # 检查数据库
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_functions = FunctionDAO.get_all()
        
        print(f"\n数据库:")
        print(f"  文件: {len(db_files)}")
        print(f"  类型: {len(db_types)}")
        for t in db_types:
            print(f"    - {t['name']} ({t.get('kind', 'unknown')})")
        print(f"  函数: {len(db_functions)}")
        for f in db_functions:
            print(f"    - {f['name']} (file_id={f['file_id']})")
        
        # 检查缓存
        print(f"\n缓存:")
        print(f"  类型缓存: {len(engine._type_cache)}")
        print(f"  函数缓存: {len(engine._function_cache)}")
        
        # 一致性检查
        print(f"\n--- 一致性检查 ---")
        types_ok = len(engine._type_cache) == len(db_types)
        functions_ok = len(engine._function_cache) == len(db_functions)
        print(f"类型: DB={len(db_types)}, Cache={len(engine._type_cache)} -> {'✓ PASS' if types_ok else '✗ FAIL'}")
        print(f"函数: DB={len(db_functions)}, Cache={len(engine._function_cache)} -> {'✓ PASS' if functions_ok else '✗ FAIL'}")
        
        # 恢复全局连接
        _restore_database()


def _isolate_database(db_conn):
    """隔离全局数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    _isolate_database.original_db = src.database.DATABASE_CONNECTION
    _isolate_database.original_dao_db = dao_module.DATABASE_CONNECTION
    
    src.database.DATABASE_CONNECTION = db_conn
    dao_module.DATABASE_CONNECTION = db_conn


def _restore_database():
    """恢复全局数据库连接"""
    import src.database
    import src.database.data_access_object as dao_module
    
    src.database.DATABASE_CONNECTION = _isolate_database.original_db
    dao_module.DATABASE_CONNECTION = _isolate_database.original_dao_db


if __name__ == "__main__":
    test_language_specific()
