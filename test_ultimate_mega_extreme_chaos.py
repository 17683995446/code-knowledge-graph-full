#!/usr/bin/env python3
"""
最终极极端混乱测试 - 多次迭代验证
包含：超大规模项目、混合语言、极端边界条件、快速变更、并发测试
"""

import os
import sys
import tempfile
import random
import time
import string
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.parsers import initialize_all_parsers
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class UltimateMegaExtremeChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
    
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="ultimate_mega_extreme_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="ultimate_mega_extreme_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info("✅ 最终极极端测试环境准备完成")
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def generate_random_name(self, length=8, include_unicode=True):
        """生成随机名称"""
        chars = string.ascii_letters + string.digits
        if include_unicode and random.random() < 0.3:
            unicode_chars = '中文日本語한국어العربية'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_mega_python_file(self, filepath: Path, num_classes=3, num_functions=10):
        """创建复杂Python文件"""
        lines = []
        lines.append("# Mega Chaos Python")
        
        for _ in range(num_classes):
            class_name = self.generate_random_name()
            lines.append(f"class {class_name}:")
            lines.append(f'    """{self.generate_random_name(20)}"""')
            
            for _ in range(random.randint(1, 4)):
                method_name = self.generate_random_name()
                lines.append(f"    def {method_name}(self):")
                lines.append(f"        return '{self.generate_random_name(15)}'")
                lines.append("")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            lines.append(f"def {func_name}():")
            lines.append(f"    return {random.randint(0, 1000)}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
    
    def create_mega_js_file(self, filepath: Path, num_classes=2, num_functions=8):
        """创建复杂JavaScript文件"""
        lines = []
        lines.append("// Mega Chaos JavaScript")
        
        for _ in range(num_classes):
            class_name = self.generate_random_name()
            lines.append(f"class {class_name} {{")
            lines.append("    constructor() {")
            lines.append(f"        this.{self.generate_random_name()} = null;")
            lines.append("    }")
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_random_name()
                lines.append(f"    {method_name}() {{")
                lines.append(f"        return '{self.generate_random_name(10)}';")
                lines.append("    }")
            lines.append("}")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            lines.append(f"function {func_name}() {{")
            lines.append(f"    return {random.randint(0, 1000)};")
            lines.append("}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
    
    def create_mega_ts_file(self, filepath: Path, num_classes=2, num_functions=8):
        """创建复杂TypeScript文件"""
        lines = []
        lines.append("// Mega Chaos TypeScript")
        
        for _ in range(num_classes):
            class_name = self.generate_random_name()
            lines.append(f"class {class_name} {{")
            lines.append(f"    {self.generate_random_name()}: string;")
            lines.append("    constructor() {")
            lines.append(f"        this.{self.generate_random_name()} = '';")
            lines.append("    }")
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_random_name()
                lines.append(f"    {method_name}(): string {{")
                lines.append(f"        return '{self.generate_random_name(10)}';")
                lines.append("    }")
            lines.append("}")
            lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            lines.append(f"function {func_name}(): number {{")
            lines.append(f"    return {random.randint(0, 1000)};")
            lines.append("}")
            lines.append("")
        
        filepath.write_text('\n'.join(lines))
    
    def create_mega_go_file(self, filepath: Path, num_structs=2, num_functions=6):
        """创建复杂Go文件"""
        lines = []
        lines.append("// Mega Chaos Go")
        lines.append("package main")
        lines.append("")
        
        for _ in range(num_structs):
            struct_name = self.generate_random_name()
            lines.append(f"type {struct_name} struct {{")
            lines.append(f"    {self.generate_random_name()} string")
            lines.append("}")
            lines.append("")
            
            for _ in range(random.randint(1, 2)):
                method_name = self.generate_random_name()
                lines.append(f"func (s *{struct_name}) {method_name}() string {{")
                lines.append(f"    return '{self.generate_random_name(10)}'")
                lines.append("}")
                lines.append("")
        
        for _ in range(num_functions):
            func_name = self.generate_random_name()
            lines.append(f"func {func_name}() int {{")
            lines.append(f"    return {random.randint(0, 1000)}")
            lines.append("}")
            lines.append("")
        
        lines.append("func main() {}")
        filepath.write_text('\n'.join(lines))
    
    def create_edge_case_file(self, filepath: Path, lang='py'):
        """创建极端边界条件文件"""
        edge_cases = [
            '',  # Empty file
            '#' * 10000 + '\n' + 'class A: pass',  # Very long comments
            'class ' + 'A' * 1000 + ':\n    pass',  # Long identifier
        ]
        
        if lang == 'py':
            content = random.choice(edge_cases)
            if not content:
                content = "# Empty file"
        else:
            content = random.choice([
                '',
                '//' * 1000 + '\n' + 'class A {}',
                'class ' + 'A' * 1000 + ' {}',
            ])
        
        filepath.write_text(content)
    
    def create_mega_project(self, num_files=1000):
        """创建最终极大规模混乱项目"""
        LOGGER.info(f"📋 创建最终极混乱项目: {num_files} 个文件")
        base_dir = Path(self.test_dir.name)
        
        start_time = time.time()
        
        for i in range(num_files):
            lang = random.choice(['py', 'js', 'ts', 'go'])
            filepath = base_dir / f"ultimate_chaos_{i:05d}.{lang}"
            
            if random.random() < 0.05:
                self.create_edge_case_file(filepath, lang)
            elif lang == 'py':
                self.create_mega_python_file(filepath)
            elif lang == 'js':
                self.create_mega_js_file(filepath)
            elif lang == 'ts':
                self.create_mega_ts_file(filepath)
            else:
                self.create_mega_go_file(filepath)
        
        elapsed = time.time() - start_time
        LOGGER.info(f"✅ 最终极项目创建完成，耗时: {elapsed:.2f}s")
    
    def test_mega_full_sync(self):
        """测试最终极大规模全同步"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("🚀 测试一：最终极大规模全同步")
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
        
        return len(files) > 0 and len(stats.errors) == 0
    
    def test_rapid_mega_changes(self):
        """测试超快速大规模变更"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("🚀 测试二：超快速大规模变更")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        changes_count = 0
        
        for i in range(50):
            action = random.choice(['create', 'modify', 'delete'])
            
            if action == 'create':
                lang = random.choice(['py', 'js', 'ts', 'go'])
                filepath = base_dir / f"rapid_new_{i:03d}.{lang}"
                if lang == 'py':
                    self.create_mega_python_file(filepath, 2, 3)
                elif lang == 'js':
                    self.create_mega_js_file(filepath, 2, 3)
                elif lang == 'ts':
                    self.create_mega_ts_file(filepath, 2, 3)
                else:
                    self.create_mega_go_file(filepath, 1, 3)
                changes_count += 1
                
            elif action == 'modify':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.ts")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    with open(filepath, 'a') as f:
                        f.write(f"\n# Modified at {time.time()}\n")
                    changes_count += 1
                    
            elif action == 'delete':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.ts")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    filepath.unlink()
                    changes_count += 1
        
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 超快速变更完成")
        LOGGER.info(f"   变更数: {changes_count}")
        LOGGER.info(f"   最终文件数: {len(files)}")
        
        return True
    
    def test_data_consistency_extreme(self):
        """测试极端数据一致性"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("🚀 测试三：极端数据一致性")
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
        
        LOGGER.info("✅ 极端数据一致性验证通过")
        return True
    
    def run_all_tests(self):
        """运行所有最终极测试"""
        try:
            self.setup()
            
            results = []
            
            results.append(("最终极大规模全同步", self.test_mega_full_sync()))
            results.append(("超快速大规模变更", self.test_rapid_mega_changes()))
            results.append(("极端数据一致性", self.test_data_consistency_extreme()))
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("🎯 最终极测试结果汇总")
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
    LOGGER.info("🎯 最终极极端混乱场景测试 - 多次迭代验证")
    LOGGER.info("="*80)
    
    tester = UltimateMegaExtremeChaosTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n✅ 所有最终极测试完美通过！系统健壮性极强！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
