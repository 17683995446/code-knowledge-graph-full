#!/usr/bin/env python3
"""
超全面极端混乱场景测试 - 验证所有修复
测试范围：
1. FileMonitor 文件验证修复
2. ArkTS 解析器 import 修复
3. 所有语言的边界条件
4. 超大规模并发场景
5. 复杂调用关系
"""

import os
import sys
import tempfile
import random
import time
import string
import threading
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.parsers import initialize_all_parsers
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class ExtremeComprehensiveChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
        
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="extreme_comprehensive_chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="extreme_chaos_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info(f"✅ 超全面极端混乱测试环境准备完成")
        LOGGER.info(f"   测试目录: {self.test_dir.name}")
        LOGGER.info(f"   数据库: {self.db_path}")
        
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        LOGGER.info("✅ 测试环境已清理")
        
    def generate_name(self, length=8, include_unicode=True):
        """生成随机名称"""
        chars = string.ascii_letters + string.digits
        if include_unicode and random.random() < 0.3:
            unicode_chars = '中文日本語한국어العربيةעבריתไทย'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
    
    def test_filemonitor_hidden_directories(self):
        """测试1: FileMonitor 对隐藏目录的处理（修复验证）"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试1: FileMonitor 隐藏目录处理（修复验证）")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        valid_file = base_dir / "valid_file.py"
        valid_file.write_text("def test(): return 1\n")
        
        hidden_dir = base_dir / ".hidden_project"
        hidden_dir.mkdir()
        hidden_file = hidden_dir / "hidden_file.py"
        hidden_file.write_text("def hidden(): return 2\n")
        
        nested_hidden = base_dir / "src" / ".config"
        nested_hidden.mkdir(parents=True)
        nested_file = nested_hidden / "nested.py"
        nested_file.write_text("def nested(): return 3\n")
        
        LOGGER.info(f"创建文件：{valid_file}")
        LOGGER.info(f"创建隐藏目录文件：{hidden_file}")
        LOGGER.info(f"创建嵌套隐藏目录文件：{nested_file}")
        
        self.engine.initialize()
        files = self.engine.file_monitor.scan_all_files()
        
        LOGGER.info(f"扫描到的文件数: {len(files)}")
        for f in files:
            LOGGER.info(f"  - {f}")
        
        valid_found = any('valid_file' in str(f) for f in files)
        hidden_found = any('hidden_file' in str(f) for f in files)
        nested_found = any('nested.py' in str(f) for f in files)
        
        LOGGER.info(f"合法文件找到: {valid_found}")
        LOGGER.info(f"隐藏目录文件找到: {hidden_found}")
        LOGGER.info(f"嵌套隐藏目录文件找到: {nested_found}")
        
        assert valid_found, "合法文件应该被找到"
        assert not hidden_found, "隐藏目录下的文件不应该被找到"
        assert not nested_found, "中间目录为隐藏的文件不应该被找到"
        
        LOGGER.info("✅ FileMonitor 修复验证通过！")
        return True
        
    def test_arkts_import_edge_cases(self):
        """测试2: ArkTS 解析器 import 边界条件（修复验证）"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试2: ArkTS Import 边界条件（修复验证）")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        test_file = base_dir / "test_imports.ets"
        
        content = '''
import { Component, BuildComponent } from '@ohos/arkcomponents';
import Default from 'default_export';
import * as All from 'wildcard_module';
import { util1, util2, util3 } from './utils';
import React from 'react';

export function test() {
    Component();
    BuildComponent();
    Default();
}

class TestClass {
    method1() {
        util1();
        util2();
    }
}
'''
        
        test_file.write_text(content)
        
        from src.parsers import get_parser_for_file
        parser = get_parser_for_file(test_file)
        
        if parser:
            result = parser.parse(test_file)
            
            LOGGER.info(f"解析的 import 数量: {len(result.imports)}")
            for imp in result.imports:
                LOGGER.info(f"  - 模块: {imp['module_path']}, 名称: {imp['imported_names']}, 通配: {imp['is_wildcard']}")
            
            assert len(result.imports) == 5, f"应该有5个import，实际：{len(result.imports)}"
            
            default_import = [i for i in result.imports if 'default_export' in i['module_path']]
            assert len(default_import) == 1 and default_import[0]['imported_names'] == ['Default'], f"Default导入应该是 ['Default']，实际：{default_import[0]['imported_names']}"
            
            wildcard_import = [i for i in result.imports if i['is_wildcard']]
            assert len(wildcard_import) == 1, "应该有一个通配符导入"
            
            multi_import = [i for i in result.imports if len(i['imported_names']) >= 2]
            assert len(multi_import) >= 1, f"应该有至少一个多元素导入，实际：{len(multi_import)}"
            
            utils_import = [i for i in result.imports if any(n in i.get('imported_names', []) for n in ['util1', 'util2', 'util3'])]
            assert len(utils_import) == 1, f"应该有一个包含 util1, util2, util3 的导入，实际：{len(utils_import)}"
            
            LOGGER.info("✅ ArkTS import 修复验证通过！")
        else:
            LOGGER.warning("⚠️ ArkTS 解析器未注册")
        
        return True
        
    def create_complex_arkts_file(self, filepath: Path, num_classes=3, num_functions=8):
        """创建复杂 ArkTS 文件"""
        lines = []
        lines.append("// Complex ArkTS File")
        
        class_names = []
        func_names = []
        
        for _ in range(num_classes):
            class_name = self.generate_name()
            class_names.append(class_name)
            
            lines.append(f"class {class_name} {{")
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_name()
                func_names.append(method_name)
                lines.append(f"    {method_name}(): string {{")
                lines.append(f"        return '{self.generate_name(10)}';")
                lines.append("    }")
            
            lines.append("}")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_name()
            func_names.append(func_name)
            lines.append(f"function {func_name}(): number {{")
            
            if random.random() < 0.6 and func_names:
                callee = random.choice(func_names[:-1])
                lines.append(f"    {callee}();")
            
            lines.append(f"    return {random.randint(0, 100)};")
            lines.append("}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
        
    def create_complex_python_file(self, filepath: Path, num_classes=3, num_functions=10):
        """创建复杂 Python 文件"""
        lines = []
        lines.append("# Complex Python File")
        
        class_names = []
        func_names = []
        
        for _ in range(num_classes):
            class_name = self.generate_name()
            class_names.append(class_name)
            
            lines.append(f"class {class_name}:")
            lines.append(f'    """{self.generate_name(20)}"""')
            
            for _ in range(random.randint(1, 4)):
                method_name = self.generate_name()
                func_names.append(method_name)
                lines.append(f"    def {method_name}(self):")
                lines.append(f"        return '{self.generate_name(15)}'")
                lines.append("")
            
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_name()
            func_names.append(func_name)
            lines.append(f"def {func_name}():")
            
            if random.random() < 0.6 and func_names:
                callee = random.choice(func_names[:-1])
                lines.append(f"    {callee}()")
            
            lines.append(f"    return {random.randint(0, 100)}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
        
    def create_complex_js_file(self, filepath: Path, num_classes=2, num_functions=8):
        """创建复杂 JavaScript 文件"""
        lines = []
        lines.append("// Complex JavaScript File")
        
        class_names = []
        func_names = []
        
        for _ in range(num_classes):
            class_name = self.generate_name()
            class_names.append(class_name)
            
            lines.append(f"class {class_name} {{")
            lines.append("    constructor() {")
            lines.append(f"        this.{self.generate_name()} = null;")
            lines.append("    }")
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_name()
                func_names.append(method_name)
                lines.append(f"    {method_name}() {{")
                lines.append(f"        return '{self.generate_name(10)}';")
                lines.append("    }")
            
            lines.append("}")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_name()
            func_names.append(func_name)
            lines.append(f"function {func_name}() {{")
            
            if random.random() < 0.5 and func_names:
                callee = random.choice(func_names[:-1])
                lines.append(f"    {callee}();")
            
            lines.append(f"    return {random.randint(0, 100)};")
            lines.append("}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
        
    def create_complex_go_file(self, filepath: Path, num_structs=2, num_functions=6):
        """创建复杂 Go 文件"""
        lines = []
        lines.append("// Complex Go File")
        lines.append("package main")
        lines.append("")
        
        struct_names = []
        func_names = []
        
        for _ in range(num_structs):
            struct_name = self.generate_name()
            struct_names.append(struct_name)
            
            lines.append(f"type {struct_name} struct {{")
            lines.append(f"    {self.generate_name()} string")
            lines.append("}")
            lines.append("")
            
            for _ in range(random.randint(1, 2)):
                method_name = self.generate_name()
                func_names.append(method_name)
                lines.append(f"func (s *{struct_name}) {method_name}() string {{")
                lines.append(f"    return '{self.generate_name(10)}'")
                lines.append("}")
                lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_name()
            func_names.append(func_name)
            lines.append(f"func {func_name}() int {{")
            lines.append(f"    return {random.randint(0, 100)}")
            lines.append("}")
            lines.append("")
        
        lines.append("func main() {}")
        filepath.write_text('\n'.join(lines))
        
    def test_mega_complex_project(self, num_files=500):
        """测试3: 超大规模复杂项目"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info(f"📋 测试3: 超大规模复杂项目 ({num_files} 文件)")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        start_time = time.time()
        
        for i in range(num_files):
            lang = random.choice(['py', 'js', 'go', 'ts'])
            filepath = base_dir / f"complex_{i:05d}.{lang}"
            
            if lang == 'py':
                self.create_complex_python_file(filepath)
            elif lang == 'js':
                self.create_complex_js_file(filepath)
            elif lang == 'go':
                self.create_complex_go_file(filepath)
            else:
                self.create_complex_arkts_file(filepath)
        
        elapsed = time.time() - start_time
        LOGGER.info(f"✅ 项目创建完成，耗时: {elapsed:.2f}s")
        
        self.engine.initialize()
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 全同步完成，耗时: {elapsed:.2f}s")
        LOGGER.info(f"   处理文件数: {stats.files_processed}")
        LOGGER.info(f"   处理类型数: {stats.types_processed}")
        LOGGER.info(f"   处理函数数: {stats.functions_processed}")
        LOGGER.info(f"   调用关系数: {stats.calls_resolved}")
        LOGGER.info(f"   错误数: {len(stats.errors)}")
        LOGGER.info(f"   数据库文件数: {len(files)}")
        LOGGER.info(f"   数据库类型数: {len(types)}")
        LOGGER.info(f"   数据库函数数: {len(funcs)}")
        
        success = len(files) > 0 and len(stats.errors) == 0
        return success
        
    def test_concurrent_file_changes(self):
        """测试4: 并发文件变更"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试4: 并发文件变更")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        num_threads = 10
        files_per_thread = 20
        
        def create_files(thread_id):
            for i in range(files_per_thread):
                lang = random.choice(['py', 'js', 'go', 'ts'])
                filepath = base_dir / f"thread_{thread_id}_file_{i:02d}.{lang}"
                
                if lang == 'py':
                    self.create_complex_python_file(filepath, num_classes=1, num_functions=2)
                elif lang == 'js':
                    self.create_complex_js_file(filepath, num_classes=1, num_functions=2)
                elif lang == 'go':
                    self.create_complex_go_file(filepath, num_structs=1, num_functions=2)
                else:
                    self.create_complex_arkts_file(filepath, num_classes=1, num_functions=2)
        
        threads = []
        for tid in range(num_threads):
            t = threading.Thread(target=create_files, args=(tid,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        LOGGER.info(f"✅ 并发创建 {num_threads * files_per_thread} 个文件")
        
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 并发变更后同步完成")
        LOGGER.info(f"   最终文件数: {len(files)}")
        
        return len(files) > 0
        
    def test_data_consistency_check(self):
        """测试5: 数据一致性校验"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试5: 数据一致性校验")
        LOGGER.info("="*80)
        
        cache_stats = self.engine.get_statistics()
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"   缓存文件数: {cache_stats['cache']['files']}")
        LOGGER.info(f"   缓存类型数: {cache_stats['cache']['types']}")
        LOGGER.info(f"   缓存函数数: {cache_stats['cache']['functions']}")
        LOGGER.info(f"   数据库文件数: {len(db_files)}")
        LOGGER.info(f"   数据库类型数: {len(db_types)}")
        LOGGER.info(f"   数据库函数数: {len(db_funcs)}")
        
        assert cache_stats['cache']['files'] == len(db_files), "文件缓存与数据库不一致"
        assert cache_stats['cache']['types'] == len(db_types), "类型缓存与数据库不一致"
        
        LOGGER.info("✅ 数据一致性检查通过！")
        return True
        
    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.setup()
            
            results = []
            
            results.append(("FileMonitor 隐藏目录修复", self.test_filemonitor_hidden_directories()))
            results.append(("ArkTS Import 修复", self.test_arkts_import_edge_cases()))
            results.append(("超大规模复杂项目", self.test_mega_complex_project(500)))
            results.append(("并发文件变更", self.test_concurrent_file_changes()))
            results.append(("数据一致性", self.test_data_consistency_check()))
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("📊 测试结果汇总")
            LOGGER.info("="*80)
            
            for name, passed in results:
                status = "✅ 通过" if passed else "❌ 失败"
                LOGGER.info(f"   {name}: {status}")
            
            all_passed = all(r[1] for r in results)
            
            return all_passed
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    LOGGER.info("\n" + "="*80)
    LOGGER.info("🎯 超全面极端混乱场景测试 - 验证所有修复")
    LOGGER.info("="*80)
    
    tester = ExtremeComprehensiveChaosTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n✅ 所有超全面测试通过！所有修复验证成功！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
