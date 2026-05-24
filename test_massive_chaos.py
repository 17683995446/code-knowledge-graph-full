#!/usr/bin/env python3
"""超大规模混乱场景压力测试 - 500+文件，深度嵌套，多轮连续修改"""

import sys
import tempfile
import random
import string
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


class MassiveChaosTestSuite:
    """超大规模混乱场景测试套件"""
    
    def __init__(self):
        self.temp_dir = None
        self.db_conn = None
        self.engine = None
        self.test_results = []
        
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 100)
        print("超大规模混乱场景压力测试")
        print("=" * 100)
        
        initialize_all_parsers()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)
            
            # 创建独立的数据库
            db_path = self.temp_dir / 'massive_chaos.db'
            self.db_conn = DatabaseConnection(db_path)
            self.db_conn.initialize_database()
            
            # 隔离全局数据库连接
            self._isolate_database()
            
            # 运行测试
            self.test_500_files_deep_nesting()
            self.test_multi_language_mixing()
            self.test_special_characters()
            self.test_corrupted_files()
            self.test_sequential_modifications()
            
            # 恢复全局连接
            self._restore_database()
            
            # 输出结果
            self._print_results()
    
    def _isolate_database(self):
        """隔离全局数据库连接"""
        import src.database
        import src.database.data_access_object as dao_module
        
        self._original_db = src.database.DATABASE_CONNECTION
        self._original_dao_db = dao_module.DATABASE_CONNECTION
        
        src.database.DATABASE_CONNECTION = self.db_conn
        dao_module.DATABASE_CONNECTION = self.db_conn
    
    def _restore_database(self):
        """恢复全局数据库连接"""
        import src.database
        import src.database.data_access_object as dao_module
        
        src.database.DATABASE_CONNECTION = self._original_db
        dao_module.DATABASE_CONNECTION = self._original_dao_db
    
    def test_500_files_deep_nesting(self):
        """测试500+文件深度嵌套场景"""
        print("\n" + "=" * 80)
        print("测试1: 500+文件深度嵌套场景")
        print("=" * 80)
        
        start_time = time.time()
        
        # 创建20层深度嵌套目录
        current_path = self.temp_dir / "deep_nesting"
        for i in range(20):
            current_path = current_path / f"level_{i}"
            current_path.mkdir(parents=True, exist_ok=True)
            
            # 每层创建多个文件
            for j in range(25):
                file_path = current_path / f"file_{j}.py"
                file_path.write_text(self._generate_python_code(f"deep_{i}_{j}"))
        
        print(f"创建完成: 500个文件，20层嵌套")
        print(f"耗时: {time.time() - start_time:.2f}s")
        
        # 初始化引擎并同步
        self.engine = IncrementalUpdateEngine(self.temp_dir / "deep_nesting")
        self.engine.initialize()
        
        sync_start = time.time()
        stats = self.engine.full_sync()
        sync_time = time.time() - sync_start
        
        print(f"\n全量同步结果:")
        print(f"  文件处理: {stats.files_processed}")
        print(f"  类型处理: {stats.types_processed}")
        print(f"  函数处理: {stats.functions_processed}")
        print(f"  同步耗时: {sync_time:.2f}s")
        
        # 验证一致性
        self._verify_consistency("深度嵌套场景")
    
    def test_multi_language_mixing(self):
        """测试多语言混合场景"""
        print("\n" + "=" * 80)
        print("测试2: 多语言混合场景")
        print("=" * 80)
        
        base_path = self.temp_dir / "multi_lang"
        base_path.mkdir(parents=True, exist_ok=True)
        
        languages = {
            '.py': self._generate_python_code,
            '.js': self._generate_javascript_code,
            '.ts': self._generate_typescript_code,
            '.jsx': self._generate_jsx_code,
            '.go': self._generate_go_code,
        }
        
        for lang, generator in languages.items():
            lang_dir = base_path / lang[1:]
            lang_dir.mkdir(parents=True, exist_ok=True)
            
            for i in range(100):
                file_path = lang_dir / f"module_{i}{lang}"
                file_path.write_text(generator(f"lang_{lang[1:]}_{i}"))
        
        print(f"创建完成: 500个文件，5种语言")
        
        # 扫描新创建的文件
        new_files = []
        for ext in languages.keys():
            new_files.extend(base_path.rglob(f"*{ext}"))
        print(f"扫描到 {len(new_files)} 个新文件")
        
        # 增量同步
        stats = self.engine.process_events(new_files)
        print(f"\n增量同步结果:")
        print(f"  文件处理: {stats.files_processed}")
        print(f"  类型处理: {stats.types_processed}")
        print(f"  函数处理: {stats.functions_processed}")
        
        self._verify_consistency("多语言混合场景")
    
    def test_special_characters(self):
        """测试特殊字符文件名"""
        print("\n" + "=" * 80)
        print("测试3: 特殊字符文件名")
        print("=" * 80)
        
        special_dir = self.temp_dir / "special_chars"
        special_dir.mkdir(parents=True, exist_ok=True)
        
        # 各种特殊字符文件名
        special_names = [
            "file with spaces.py",
            "file-with-dashes.py",
            "file_with_underscores.py",
            "file.with.dots.py",
            "file_with_中文.py",
            "文件中文.py",
            "файл.py",
            "αρχείο.py",
            "file@#$%.py",
            "file[brackets].py",
        ]
        
        for name in special_names:
            try:
                file_path = special_dir / name
                file_path.write_text(self._generate_python_code(f"special_{name}"))
            except Exception as e:
                print(f"  跳过无效文件名 {name}: {e}")
        
        print(f"创建完成: {len(special_names)}个特殊字符文件")
        
        # 增量同步
        stats = self.engine.process_events(list(special_dir.glob("*.py")))
        print(f"\n增量同步结果:")
        print(f"  文件处理: {stats.files_processed}")
        
        self._verify_consistency("特殊字符场景")
    
    def test_corrupted_files(self):
        """测试损坏/无效文件"""
        print("\n" + "=" * 80)
        print("测试4: 损坏/无效文件场景")
        print("=" * 80)
        
        corrupted_dir = self.temp_dir / "corrupted"
        corrupted_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建各种无效文件
        invalid_files = [
            corrupted_dir / "empty.py",
            corrupted_dir / "binary.bin",
            corrupted_dir / "huge.py",
        ]
        
        # 空文件
        invalid_files[0].write_text("")
        
        # 二进制文件
        invalid_files[1].write_bytes(b'\x00\x01\x02\x03\xff\xfe\xfd')
        
        # 超大文件（故意让解析器超时或失败）
        invalid_files[2].write_text("# " + "x" * 1000000)
        
        print(f"创建完成: {len(invalid_files)}个无效文件")
        
        # 增量同步
        stats = self.engine.process_events(invalid_files)
        print(f"\n增量同步结果:")
        print(f"  文件处理: {stats.files_processed}")
        print(f"  错误数: {len(stats.errors)}")
        
        self._verify_consistency("无效文件场景")
    
    def test_sequential_modifications(self):
        """测试连续多轮修改（10轮）"""
        print("\n" + "=" * 80)
        print("测试5: 连续10轮修改场景")
        print("=" * 80)
        
        mod_dir = self.temp_dir / "sequential"
        mod_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建初始文件
        test_file = mod_dir / "dynamic.py"
        test_file.write_text(self._generate_python_code("initial"))
        
        # 初始同步
        self.engine.process_events([test_file])
        
        print("\n开始10轮连续修改:")
        for round_num in range(1, 11):
            # 每轮修改文件内容
            new_content = self._generate_python_code(f"round_{round_num}")
            test_file.write_text(new_content)
            
            # 增量更新
            stats = self.engine.process_events([test_file])
            
            print(f"  轮次 {round_num}: 类型={stats.types_processed}, 函数={stats.functions_processed}")
            
            # 验证一致性
            consistent = self._verify_consistency(f"轮次 {round_num}", silent=True)
            if not consistent:
                print(f"    ⚠️  发现不一致!")
                break
            
            # 每3轮删除并重建一次
            if round_num % 3 == 0:
                test_file.unlink()
                stats = self.engine.process_events([test_file])
                print(f"    删除文件: 类型={stats.types_processed}, 函数={stats.functions_processed}")
                
                test_file.write_text(self._generate_python_code(f"regenerated_{round_num}"))
                stats = self.engine.process_events([test_file])
                print(f"    重建文件: 类型={stats.types_processed}, 函数={stats.functions_processed}")
        
        print("\n连续修改测试完成!")
        self._verify_consistency("连续10轮修改")
    
    def _verify_consistency(self, stage_name, silent=False):
        """验证缓存与数据库一致性"""
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_functions = FunctionDAO.get_all()
        
        cache_types = len(self.engine._type_cache)
        cache_functions = len(self.engine._function_cache)
        
        types_ok = cache_types == len(db_types)
        functions_ok = cache_functions == len(db_functions)
        
        if not silent:
            print(f"\n【{stage_name} 一致性检查】")
            print(f"  数据库: {len(db_files)}文件, {len(db_types)}类型, {len(db_functions)}函数")
            print(f"  缓存:   {cache_types}类型, {cache_functions}函数")
            print(f"  类型: {'✓ PASS' if types_ok else '✗ FAIL'}")
            print(f"  函数: {'✓ PASS' if functions_ok else '✗ FAIL'}")
        
        result = {
            'stage': stage_name,
            'types_ok': types_ok,
            'functions_ok': functions_ok,
            'db_files': len(db_files),
            'db_types': len(db_types),
            'db_functions': len(db_functions),
            'cache_types': cache_types,
            'cache_functions': cache_functions,
        }
        self.test_results.append(result)
        
        return types_ok and functions_ok
    
    def _print_results(self):
        """打印测试结果总结"""
        print("\n" + "=" * 100)
        print("测试结果总结")
        print("=" * 100)
        
        all_passed = True
        for result in self.test_results:
            status = "✓ PASS" if (result['types_ok'] and result['functions_ok']) else "✗ FAIL"
            if result['types_ok'] and result['functions_ok']:
                print(f"{status} | {result['stage']}")
            else:
                print(f"{status} | {result['stage']} | DB: {result['db_types']}T/{result['db_functions']}F | Cache: {result['cache_types']}T/{result['cache_functions']}F")
                all_passed = False
        
        print("\n" + "=" * 100)
        if all_passed:
            print("🎉 所有测试通过！系统在大规模混乱场景下表现正常")
        else:
            print("⚠️  发现问题！需要进一步调查")
        print("=" * 100)
    
    def _generate_python_code(self, name):
        """生成Python代码"""
        return f'''
class {name.title().replace('_', '')}:
    """Generated test class {name}"""
    
    def __init__(self):
        self.data = []
    
    def process(self, value):
        """Process a value"""
        return value * 2
    
    def validate(self):
        """Validate data"""
        return len(self.data) > 0


def {name.replace('-', '_')}_helper(x, y):
    """Helper function"""
    return x + y


def {name.replace('-', '_')}_processor(data):
    """Process data"""
    result = []
    for item in data:
        result.append(item * 3)
    return result
'''
    
    def _generate_javascript_code(self, name):
        """生成JavaScript代码"""
        return f'''
class {name.replace('-', '').title()} {{
    constructor() {{
        this.data = [];
    }}
    
    process(value) {{
        return value * 2;
    }}
    
    validate() {{
        return this.data.length > 0;
    }}
}}

export function {name.replace('-', '_')}_helper(x, y) {{
    return x + y;
}}

export function {name.replace('-', '_')}_processor(data) {{
    return data.map(item => item * 3);
}}
'''
    
    def _generate_typescript_code(self, name):
        """生成TypeScript代码"""
        return f'''
class {name.replace('-', '').title()} {{
    private data: any[] = [];
    
    process(value: any): any {{
        return value * 2;
    }}
    
    validate(): boolean {{
        return this.data.length > 0;
    }}
}}

export function {name.replace('-', '_')}_helper<T>(x: T, y: T): T {{
    return x as any + y as any;
}}
'''
    
    def _generate_jsx_code(self, name):
        """生成JSX代码"""
        return f'''
import React from 'react';

export function {name.replace('-', '_')}_Component() {{
    return <div>{name}</div>;
}}

export function {name.replace('-', '_')}_helper(x, y) {{
    return x + y;
}}
'''
    
    def _generate_go_code(self, name):
        """生成Go代码"""
        safe_name = name.replace('-', '')
        return f'''
package main

type {safe_name.title()} struct {{
    Data []interface{{}}
}}

func (c *{safe_name.title()}) Process(value interface{{}}) interface{{}} {{
    return value
}}

func {name.replace('-', '_')}_helper(x, y interface{{}}) interface{{}} {{
    return x
}}

func {name.replace('-', '_')}_processor(data []interface{{}}) []interface{{}} {{
    return data
}}
'''


def main():
    """主函数"""
    test_suite = MassiveChaosTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
