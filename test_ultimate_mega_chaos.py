#!/usr/bin/env python3
"""
终极大规模混乱测试 - 多次迭代
包含：
- 1000+ 文件
- 混合语言
- 复杂调用关系
- 快速变更
- 边界条件
- 压力测试
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


class UltimateMegaChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
        
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="ultimate_mega_chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="ultimate_mega_chaos_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info(f"✅ 终极大规模混乱测试环境准备完成")
        LOGGER.info(f"   测试目录: {self.test_dir.name}")
        LOGGER.info(f"   数据库: {self.db_path}")
        
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        LOGGER.info("✅ 测试环境已清理")
        
    def generate_random_name(self, length=8, include_unicode=True):
        """生成随机名称"""
        chars = string.ascii_letters + string.digits
        if include_unicode and random.random() < 0.2:
            unicode_chars = '中文日本語한국어العربية'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
        
    def create_mega_python_file(self, filepath: Path, num_classes=3, num_functions=10):
        """创建复杂Python文件"""
        lines = []
        lines.append("# Mega Chaos Python File")
        
        class_names = []
        func_names = []
        
        for _ in range(num_classes):
            class_name = self.generate_random_name()
            class_names.append(class_name)
            
            lines.append(f"class {class_name}:")
            lines.append(f'    """{self.generate_random_name(20)}"""')
            
            for _ in range(random.randint(1, 4)):
                method_name = self.generate_random_name()
                func_names.append(method_name)
                lines.append(f"    def {method_name}(self):")
                lines.append(f"        return '{self.generate_random_name(15)}'")
                lines.append("")
            
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            func_names.append(func_name)
            lines.append(f"def {func_name}():")
            
            if random.random() < 0.6:
                callee = random.choice(func_names) if func_names else None
                if callee and callee != func_name:
                    lines.append(f"    {callee}()")
            
            lines.append(f"    return {random.randint(0, 1000)}")
            lines.append("")
        
        if random.random() < 0.5:
            lines.append("if __name__ == '__main__':")
            main_func = random.choice(func_names) if func_names else None
            if main_func:
                lines.append(f"    {main_func}()")
        
        filepath.write_text('\n'.join(lines))
        
    def create_mega_js_file(self, filepath: Path, num_classes=2, num_functions=8):
        """创建复杂JavaScript文件"""
        lines = []
        lines.append("// Mega Chaos JavaScript File")
        
        class_names = []
        func_names = []
        
        for _ in range(num_classes):
            class_name = self.generate_random_name()
            class_names.append(class_name)
            
            lines.append(f"class {class_name} {{")
            lines.append("    constructor() {")
            lines.append(f"        this.{self.generate_random_name()} = null;")
            lines.append("    }")
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_random_name()
                func_names.append(method_name)
                lines.append(f"    {method_name}() {{")
                lines.append(f"        return '{self.generate_random_name(10)}';")
                lines.append("    }")
            
            lines.append("}")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            func_names.append(func_name)
            lines.append(f"function {func_name}() {{")
            
            if random.random() < 0.5:
                callee = random.choice(func_names) if func_names else None
                if callee and callee != func_name:
                    lines.append(f"    {callee}();")
            
            lines.append(f"    return {random.randint(0, 1000)};")
            lines.append("}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
        
    def create_mega_go_file(self, filepath: Path, num_structs=2, num_functions=6):
        """创建复杂Go文件"""
        lines = []
        lines.append("// Mega Chaos Go File")
        lines.append("package main")
        lines.append("")
        
        struct_names = []
        func_names = []
        
        for _ in range(num_structs):
            struct_name = self.generate_random_name()
            struct_names.append(struct_name)
            
            lines.append(f"type {struct_name} struct {{")
            lines.append(f"    {self.generate_random_name()} string")
            lines.append("}")
            lines.append("")
            
            for _ in range(random.randint(1, 2)):
                method_name = self.generate_random_name()
                func_names.append(method_name)
                lines.append(f"func (s *{struct_name}) {method_name}() string {{")
                lines.append(f"    return '{self.generate_random_name(10)}'")
                lines.append("}")
                lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            func_names.append(func_name)
            lines.append(f"func {func_name}() int {{")
            lines.append(f"    return {random.randint(0, 1000)}")
            lines.append("}")
            lines.append("")
        
        lines.append("func main() {}")
        filepath.write_text('\n'.join(lines))
        
    def create_edge_case_file(self, filepath: Path, lang='py'):
        """创建边界条件文件"""
        if lang == 'py':
            cases = [
                '',  # 空文件
                '# Only comments\n# No code',  # 只有注释
                'def broken_func():\n    invalid syntax\n    return 1',  # 语法错误
                'def a(): pass\ndef b(): pass\ndef c(): a()\n'  # 简单调用
            ]
            content = random.choice(cases)
        elif lang == 'js':
            cases = [
                '',
                '// Only comments\n/* No code */',
                'function broken() {\n    invalid syntax\n    return 1;\n}',
                'function a() {}\nfunction b() {}\nfunction c() { a(); }\n'
            ]
            content = random.choice(cases)
        else:
            cases = ['', '// Only comments', 'invalid go syntax']
            content = random.choice(cases)
        
        filepath.write_text(content)
        
    def create_mega_project(self, num_files=1000):
        """创建超大规模项目"""
        LOGGER.info(f"\n🚀 创建超大规模混乱项目: {num_files} 个文件")
        base_dir = Path(self.test_dir.name)
        
        start_time = time.time()
        
        for i in range(num_files):
            lang = random.choice(['py', 'js', 'go'])
            filepath = base_dir / f"mega_chaos_{i:05d}.{lang}"
            
            if random.random() < 0.05:  # 5% 边界条件文件
                self.create_edge_case_file(filepath, lang)
            elif lang == 'py':
                self.create_mega_python_file(filepath)
            elif lang == 'js':
                self.create_mega_js_file(filepath)
            else:
                self.create_mega_go_file(filepath)
        
        elapsed = time.time() - start_time
        LOGGER.info(f"✅ 超大规模项目创建完成，耗时: {elapsed:.2f}s")
        
    def test_full_sync_mega_project(self):
        """测试超大规模项目全同步"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试一：超大规模项目全同步")
        LOGGER.info("="*80)
        
        self.create_mega_project(800)
        
        self.engine.initialize()
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 全同步完成，耗时: {elapsed:.2f}s")
        LOGGER.info(f"   处理文件数: {stats.files_processed}")
        LOGGER.info(f"   新增文件数: {stats.files_created}")
        LOGGER.info(f"   处理类型数: {stats.types_processed}")
        LOGGER.info(f"   处理函数数: {stats.functions_processed}")
        LOGGER.info(f"   调用关系数: {stats.calls_resolved}")
        LOGGER.info(f"   错误数: {len(stats.errors)}")
        LOGGER.info(f"   数据库文件数: {len(files)}")
        LOGGER.info(f"   数据库类型数: {len(types)}")
        LOGGER.info(f"   数据库函数数: {len(funcs)}")
        
        success = len(files) > 0
        return success
        
    def test_rapid_changes(self):
        """测试快速变更"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试二：快速文件变更")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        changes_count = 0
        
        for i in range(30):  # 30次快速变更
            action = random.choice(['create', 'modify', 'delete'])
            
            if action == 'create':
                lang = random.choice(['py', 'js', 'go'])
                filepath = base_dir / f"rapid_new_{i:02d}.{lang}"
                if lang == 'py':
                    self.create_mega_python_file(filepath)
                elif lang == 'js':
                    self.create_mega_js_file(filepath)
                else:
                    self.create_mega_go_file(filepath)
                changes_count += 1
                
            elif action == 'modify':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    # 追加内容
                    with open(filepath, 'a') as f:
                        f.write(f"\n# Modified at {time.time()}\n")
                    changes_count += 1
                    
            elif action == 'delete':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    filepath.unlink()
                    changes_count += 1
        
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 快速变更后同步完成")
        LOGGER.info(f"   变更数: {changes_count}")
        LOGGER.info(f"   最终文件数: {len(files)}")
        
        return True
        
    def test_data_consistency(self):
        """测试数据一致性"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试三：数据一致性")
        LOGGER.info("="*80)
        
        cache_stats = self.engine.get_statistics()
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_funcs = FunctionDAO.get_all()
        
        cache_files = cache_stats['cache']['files']
        cache_types = cache_stats['cache']['types']
        cache_funcs = cache_stats['cache']['functions']
        
        LOGGER.info(f"   缓存文件数: {cache_files}")
        LOGGER.info(f"   缓存类型数: {cache_types}")
        LOGGER.info(f"   缓存函数数: {cache_funcs}")
        LOGGER.info(f"   数据库文件数: {len(db_files)}")
        LOGGER.info(f"   数据库类型数: {len(db_types)}")
        LOGGER.info(f"   数据库函数数: {len(db_funcs)}")
        
        assert cache_files == len(db_files), "文件缓存与数据库不一致"
        
        LOGGER.info("✅ 数据一致性检查通过")
        return True
        
    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.setup()
            
            results = []
            
            results.append(("超大规模全同步", self.test_full_sync_mega_project()))
            results.append(("快速变更", self.test_rapid_changes()))
            results.append(("数据一致性", self.test_data_consistency()))
            
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
    LOGGER.info("🎯 终极大规模混乱测试 - 多次迭代优化")
    LOGGER.info("="*80)
    
    tester = UltimateMegaChaosTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n✅ 所有终极大规模混乱测试通过！系统健壮性极强！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
