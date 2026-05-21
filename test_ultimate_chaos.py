#!/usr/bin/env python3
"""
终极混乱场景测试 - 多次迭代发现并修复真实运行时 Bug
包含：超大规模项目、混合语言、快速变更、复杂依赖、混乱命名、Unicode
"""

import os
import sys
import tempfile
import random
import time
import string
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER, CONFIG
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.parsers import initialize_all_parsers
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class UltimateChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
        
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="ultimate_chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="ultimate_chaos_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info(f"✅ 终极混乱测试环境准备完成")
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
        """生成随机名称，可能包含Unicode"""
        chars = string.ascii_letters + string.digits
        if include_unicode and random.random() < 0.3:
            unicode_chars = '中文日本語한국어العربية'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_chaos_python_file(self, filepath: Path, idx: int):
        """创建复杂的Python文件"""
        class_names = [self.generate_random_name() for _ in range(random.randint(1, 5))]
        func_names = [self.generate_random_name() for _ in range(random.randint(2, 10))]
        
        code_lines = []
        code_lines.append(f'# File {idx} - Chaos Python')
        code_lines.append('')
        
        for i, class_name in enumerate(class_names):
            code_lines.append(f'class {class_name}:')
            code_lines.append(f'    """{self.generate_random_name(20)}"""')
            code_lines.append('    def __init__(self):')
            code_lines.append(f'        self.{self.generate_random_name()} = None')
            code_lines.append('')
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_random_name()
                code_lines.append(f'    def {method_name}(self):')
                code_lines.append(f'        return "{self.generate_random_name(15)}"')
                code_lines.append('')
        
        for func_name in func_names:
            code_lines.append(f'def {func_name}():')
            code_lines.append(f'    return {random.randint(0, 100)}')
            code_lines.append('')
        
        if random.random() < 0.5:
            code_lines.append('if __name__ == "__main__":')
            code_lines.append(f'    print({random.choice(func_names)}())')
        
        filepath.write_text('\n'.join(code_lines))
    
    def create_chaos_javascript_file(self, filepath: Path, idx: int):
        """创建复杂的JavaScript文件"""
        class_names = [self.generate_random_name() for _ in range(random.randint(1, 4))]
        func_names = [self.generate_random_name() for _ in range(random.randint(2, 8))]
        
        code_lines = []
        code_lines.append(f'// File {idx} - Chaos JavaScript')
        code_lines.append('')
        
        for i, class_name in enumerate(class_names):
            code_lines.append(f'class {class_name} {{')
            code_lines.append('    constructor() {')
            code_lines.append(f'        this.{self.generate_random_name()} = null;')
            code_lines.append('    }')
            
            for _ in range(random.randint(1, 3)):
                method_name = self.generate_random_name()
                code_lines.append(f'    {method_name}() {{')
                code_lines.append(f'        return "{self.generate_random_name(10)}";')
                code_lines.append('    }')
            
            code_lines.append('}')
            code_lines.append('')
        
        for func_name in func_names:
            code_lines.append(f'function {func_name}() {{')
            code_lines.append(f'    return {random.randint(0, 100)};')
            code_lines.append('}')
            code_lines.append('')
        
        filepath.write_text('\n'.join(code_lines))
    
    def create_chaos_go_file(self, filepath: Path, idx: int):
        """创建复杂的Go文件"""
        struct_names = [self.generate_random_name() for _ in range(random.randint(1, 3))]
        func_names = [self.generate_random_name() for _ in range(random.randint(1, 5))]
        
        code_lines = []
        code_lines.append(f'// File {idx} - Chaos Go')
        code_lines.append('package main')
        code_lines.append('')
        
        for struct_name in struct_names:
            code_lines.append(f'type {struct_name} struct {{')
            code_lines.append(f'    {self.generate_random_name()} string')
            code_lines.append('}')
            code_lines.append('')
            
            for _ in range(random.randint(1, 2)):
                method_name = self.generate_random_name()
                code_lines.append(f'func (s *{struct_name}) {method_name}() string {{')
                code_lines.append(f'    return "{self.generate_random_name(10)}"')
                code_lines.append('}')
                code_lines.append('')
        
        for func_name in func_names:
            code_lines.append(f'func {func_name}() int {{')
            code_lines.append(f'    return {random.randint(0, 100)}')
            code_lines.append('}')
            code_lines.append('')
        
        code_lines.append('func main() {}')
        filepath.write_text('\n'.join(code_lines))
    
    def create_large_test_project(self, num_files=200):
        """创建超大规模混乱项目"""
        LOGGER.info(f"\n📋 创建超大规模混乱项目: {num_files} 个文件")
        base_dir = Path(self.test_dir.name)
        
        languages = ['py', 'js', 'go']
        for i in range(num_files):
            lang = random.choice(languages)
            filepath = base_dir / f"chaos_{i:04d}.{lang}"
            
            if lang == 'py':
                self.create_chaos_python_file(filepath, i)
            elif lang == 'js':
                self.create_chaos_javascript_file(filepath, i)
            else:
                self.create_chaos_go_file(filepath, i)
        
        LOGGER.info(f"✅ 创建完成: {num_files} 个文件")
    
    def test_full_sync_large_project(self):
        """测试大规模项目全量同步"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 1：超大规模项目全量同步")
        LOGGER.info("="*80)
        
        self.create_large_test_project(200)
        
        self.engine.initialize()
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 全量同步完成！")
        LOGGER.info(f"   处理文件数: {stats.files_processed}")
        LOGGER.info(f"   新增文件数: {stats.files_created}")
        LOGGER.info(f"   处理类型数: {stats.types_processed}")
        LOGGER.info(f"   处理函数数: {stats.functions_processed}")
        LOGGER.info(f"   解析调用数: {stats.calls_resolved}")
        LOGGER.info(f"   数据库文件数: {len(files)}")
        LOGGER.info(f"   数据库类型数: {len(types)}")
        LOGGER.info(f"   数据库函数数: {len(funcs)}")
        
        return len(files) > 0
    
    def test_rapid_changes(self):
        """测试快速变更场景"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 2：快速文件变更场景")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        changes_count = 0
        
        for i in range(10):
            action = random.choice(['modify', 'create', 'delete'])
            
            if action == 'create':
                lang = random.choice(['py', 'js', 'go'])
                filepath = base_dir / f"new_chaos_{i:02d}.{lang}"
                if lang == 'py':
                    self.create_chaos_python_file(filepath, i + 200)
                elif lang == 'js':
                    self.create_chaos_javascript_file(filepath, i + 200)
                else:
                    self.create_chaos_go_file(filepath, i + 200)
                changes_count += 1
                LOGGER.debug(f"  创建文件: {filepath}")
                
            elif action == 'modify':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    # 追加内容
                    with open(filepath, 'a') as f:
                        f.write(f"\n# Modified at {time.time()}\n")
                    changes_count += 1
                    LOGGER.debug(f"  修改文件: {filepath}")
                    
            elif action == 'delete':
                existing_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + list(base_dir.glob("*.go"))
                if existing_files:
                    filepath = random.choice(existing_files)
                    filepath.unlink()
                    changes_count += 1
                    LOGGER.debug(f"  删除文件: {filepath}")
        
        # 重新同步
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 快速变更后同步完成！")
        LOGGER.info(f"   变更数: {changes_count}")
        LOGGER.info(f"   最终文件数: {len(files)}")
        
        return True
    
    def test_data_consistency(self):
        """测试数据一致性"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 3：数据一致性校验")
        LOGGER.info("="*80)
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        # 验证缓存与数据库一致性
        cache_stats = self.engine.get_statistics()
        LOGGER.info(f"   缓存文件数: {cache_stats['cache']['files']}")
        LOGGER.info(f"   缓存类型数: {cache_stats['cache']['types']}")
        LOGGER.info(f"   缓存函数数: {cache_stats['cache']['functions']}")
        LOGGER.info(f"   数据库文件数: {len(files)}")
        LOGGER.info(f"   数据库类型数: {len(types)}")
        LOGGER.info(f"   数据库函数数: {len(funcs)}")
        
        # 基础验证
        assert len(files) == cache_stats['cache']['files'], "文件缓存与数据库不一致"
        
        LOGGER.info("✅ 数据一致性校验通过！")
        return True
    
    def test_empty_and_edge_files(self):
        """测试边界文件"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 4：边界文件处理")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        # 空文件
        (base_dir / "empty.py").write_text("")
        (base_dir / "empty.js").write_text("")
        (base_dir / "empty.go").write_text("")
        
        # 只有注释
        (base_dir / "comments.py").write_text("# Only comments\n# No code")
        (base_dir / "comments.js").write_text("// Only comments\n/* No code */")
        
        # 损坏的文件
        (base_dir / "broken.py").write_text("def broken(): \n    this is broken")
        (base_dir / "broken.js").write_text("function broken() { \n    this is broken }")
        
        LOGGER.info("✅ 边界文件创建完成")
        
        # 重新同步
        stats = self.engine.full_sync()
        
        LOGGER.info(f"   处理边界文件数: {stats.files_processed}")
        LOGGER.info(f"   错误数: {len(stats.errors)}")
        
        return True
    
    def run_all_iterations(self):
        """运行所有迭代测试"""
        try:
            self.setup()
            
            # 迭代1：大规模项目
            LOGGER.info("\n🚀 ====== 迭代 1：超大规模项目同步 ======")
            result1 = self.test_full_sync_large_project()
            
            # 迭代2：快速变更
            LOGGER.info("\n🚀 ====== 迭代 2：快速文件变更 ======")
            result2 = self.test_rapid_changes()
            
            # 迭代3：数据一致性
            LOGGER.info("\n🚀 ====== 迭代 3：数据一致性 ======")
            result3 = self.test_data_consistency()
            
            # 迭代4：边界文件
            LOGGER.info("\n🚀 ====== 迭代 4：边界文件 ======")
            result4 = self.test_empty_and_edge_files()
            
            return all([result1, result2, result3, result4])
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    LOGGER.info("\n" + "="*80)
    LOGGER.info("🎯 终极混乱场景测试 - 多次迭代")
    LOGGER.info("="*80)
    
    tester = UltimateChaosTester()
    success = tester.run_all_iterations()
    
    if success:
        LOGGER.info("\n✅ 所有测试通过！系统健壮性验证完成！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！需要进一步修复")
        sys.exit(1)


if __name__ == "__main__":
    main()
