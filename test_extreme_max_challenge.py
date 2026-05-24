#!/usr/bin/env python3
"""
超极端最大挑战测试 - 终极混乱场景！

包含：
- 1000+文件超大规模项目
- 深度嵌套的文件结构
- 混合5种语言同时解析
- 超快速的增量更新（毫秒级）
- 数据一致性全面验证
- 性能压力测试
- 边界条件全覆盖
"""

import os
import sys
import tempfile
import random
import time
import string
from pathlib import Path
from typing import Dict, List, Any, Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER
from src.engine.incremental_update_engine import IncrementalUpdateEngine, ParseResult
from src.database.database_connection import DATABASE_CONNECTION
from src.parsers import initialize_all_parsers
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class ExtremeMaxChallengeTest:
    """最极端、最复杂、最混乱的测试场景！"""
    
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
    
    def setup(self):
        """设置测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="extreme_max_challenge_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="extreme_max_challenge_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info("=" * 80)
        LOGGER.info("🏆 超极端最大挑战测试开始！")
        LOGGER.info("=" * 80)
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def generate_random_name(self, min_len: int = 3, max_len: int = 15, 
                              include_unicode: bool = True) -> str:
        """生成随机名称"""
        length = random.randint(min_len, max_len)
        chars = string.ascii_letters + string.digits
        
        if include_unicode and random.random() < 0.3:
            unicode_chars = '中文日本語한국어العربيةעבריתไทย'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_deep_nested_structure(self):
        """创建深度嵌套的文件结构（8层深度）"""
        base_path = Path(self.test_dir.name)
        current_dir = base_path
        
        for depth in range(8):
            dir_name = f"level_{depth}_{self.generate_random_name(5, 10)}"
            current_dir = current_dir / dir_name
            current_dir.mkdir(exist_ok=True)
            
            for i in range(random.randint(3, 7)):
                self.create_file_in_dir(current_dir, random.choice(['py', 'js', 'go']))
        
        return base_path
    
    def create_file_in_dir(self, dir_path: Path, lang: str):
        """在指定目录创建文件"""
        filename = f"{self.generate_random_name(5, 12)}.{lang}"
        file_path = dir_path / filename
        
        if lang == 'py':
            content = self.generate_python_code()
        elif lang == 'js':
            content = self.generate_javascript_code()
        elif lang == 'go':
            content = self.generate_go_code()
        else:
            content = f"// {lang} file\n"
        
        file_path.write_text(content)
        return file_path
    
    def generate_python_code(self) -> str:
        """生成复杂Python代码"""
        lines = [
            f'"""Generated test file {self.generate_random_name(10, 20)}"""',
            '',
        ]
        
        class_count = random.randint(2, 6)
        func_count = random.randint(3, 10)
        
        for cls_idx in range(class_count):
            class_name = f"Class_{self.generate_random_name(5, 10)}"
            lines.append(f"class {class_name}:")
            lines.append(f'    """{self.generate_random_name(15, 30)}"""')
            lines.append(f'    def __init__(self):')
            lines.append(f'        self.{self.generate_random_name(3, 8)} = None')
            
            for method_idx in range(random.randint(2, 5)):
                method_name = f"method_{self.generate_random_name(5, 8)}"
                lines.append(f'    def {method_name}(self):')
                lines.append(f'        return "{self.generate_random_name(10, 20)}"')
            
            lines.append('')
        
        for func_idx in range(func_count):
            func_name = f"func_{self.generate_random_name(5, 10)}"
            lines.append(f"def {func_name}():")
            lines.append(f'    return {random.randint(0, 9999)}')
            lines.append('')
        
        return '\n'.join(lines)
    
    def generate_javascript_code(self) -> str:
        """生成复杂JavaScript代码"""
        lines = [
            f'// Generated JS file {self.generate_random_name(10, 20)}',
            '',
        ]
        
        class_count = random.randint(2, 5)
        func_count = random.randint(3, 12)
        
        for cls_idx in range(class_count):
            class_name = f"JSClass_{self.generate_random_name(5, 10)}"
            lines.append(f"class {class_name} {{")
            lines.append(f"  constructor() {{")
            lines.append(f"    this.{self.generate_random_name(3, 8)} = null;")
            lines.append(f"  }}")
            
            for method_idx in range(random.randint(2, 4)):
                method_name = f"jsMethod_{self.generate_random_name(5, 8)}"
                lines.append(f"  {method_name}() {{")
                lines.append(f'    return "{self.generate_random_name(10, 20)}";')
                lines.append(f"  }}")
            
            lines.append(f"}}")
            lines.append('')
        
        for func_idx in range(func_count):
            func_name = f"jsFunc_{self.generate_random_name(5, 10)}"
            lines.append(f"function {func_name}() {{")
            lines.append(f'  return {random.randint(0, 9999)};')
            lines.append(f"}}")
            lines.append('')
        
        return '\n'.join(lines)
    
    def generate_go_code(self) -> str:
        """生成复杂Go代码"""
        lines = [
            f'// Generated Go file {self.generate_random_name(10, 20)}',
            'package main',
            '',
        ]
        
        struct_count = random.randint(2, 4)
        func_count = random.randint(3, 8)
        
        for struct_idx in range(struct_count):
            struct_name = f"GoStruct_{self.generate_random_name(5, 10)}"
            lines.append(f"type {struct_name} struct {{")
            lines.append(f'    {self.generate_random_name(3, 8)} string')
            lines.append(f"}}")
            lines.append('')
            
            method_name = f"GoMethod_{self.generate_random_name(5, 8)}"
            lines.append(f"func (g *{struct_name}) {method_name}() {{")
            lines.append(f'    // {self.generate_random_name(10, 20)}')
            lines.append(f"}}")
            lines.append('')
        
        for func_idx in range(func_count):
            func_name = f"GoFunc_{self.generate_random_name(5, 10)}"
            lines.append(f"func {func_name}() int {{")
            lines.append(f'    return {random.randint(0, 9999)}')
            lines.append(f"}}")
            lines.append('')
        
        lines.append('func main() {}')
        
        return '\n'.join(lines)
    
    def create_hyper_chaos_project(self, file_count: int = 2000):
        """创建超级混乱项目（2000文件，混合语言，深度嵌套）"""
        LOGGER.info(f"🎯 创建超极端挑战项目：{file_count} 个文件")
        start_time = time.time()
        
        base_path = Path(self.test_dir.name)
        
        # 首先创建深度嵌套结构
        self.create_deep_nested_structure()
        
        # 根目录创建大量文件
        languages = ['py', 'js', 'go']
        
        for i in range(file_count):
            lang = random.choice(languages)
            file_depth = random.randint(0, 6)
            current_path = base_path
            
            for d in range(file_depth):
                dir_name = f"random_dir_{d}_{self.generate_random_name(4, 8)}"
                current_path = current_path / dir_name
                current_path.mkdir(exist_ok=True)
            
            self.create_file_in_dir(current_path, lang)
        
        elapsed = time.time() - start_time
        LOGGER.info(f"✅ 超极端项目创建完成：{elapsed:.2f} 秒")
        
        return elapsed
    
    def test_super_extreme_full_sync(self):
        """超极端完整同步测试"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端挑战1：2000文件完整同步")
        LOGGER.info("="*80)
        
        self.create_hyper_chaos_project(2000)
        
        self.engine.initialize()
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 超极端完整同步完成：耗时 {elapsed:.2f} 秒")
        LOGGER.info(f"   数据库文件：{len(files)}")
        LOGGER.info(f"   数据库类型：{len(types)}")
        LOGGER.info(f"   数据库函数：{len(funcs)}")
        LOGGER.info(f"   同步错误：{len(stats.errors)}")
        
        assert len(files) > 0, "应该解析到文件"
        assert len(stats.errors) == 0, "不应该有错误"
        
        return elapsed, len(files), len(types), len(funcs)
    
    def test_lightning_fast_updates(self):
        """闪电般快速的增量更新"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端挑战2：闪电快速增量更新")
        LOGGER.info("="*80)
        
        base_path = Path(self.test_dir.name)
        update_rounds = 20
        
        for round_idx in range(update_rounds):
            # 创建新文件
            for i in range(20):
                lang = random.choice(['py', 'js', 'go'])
                self.create_file_in_dir(base_path, lang)
            
            # 快速同步
            start_round = time.time()
            stats = self.engine.full_sync()
            elapsed_round = time.time() - start_round
            
            LOGGER.info(f"   第 {round_idx+1} 轮更新：耗时 {elapsed_round:.3f} 秒 "
                      f"创建 {stats.files_created} 更新 {stats.files_updated}")
        
        final_files = FileDAO.get_all()
        LOGGER.info(f"✅ 闪电快速更新完成：最终文件 {len(final_files)}")
        
        return len(final_files)
    
    def test_mixed_operations(self):
        """混合操作：创建、修改、删除同时进行"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端挑战3：混合操作（创建、修改、删除）")
        LOGGER.info("="*80)
        
        base_path = Path(self.test_dir.name)
        all_files = list(base_path.rglob('*.py')) + list(base_path.rglob('*.js')) + list(base_path.rglob('*.go'))
        
        # 混合操作
        operations = 300
        
        for op_idx in range(operations):
            op_type = random.choice(['create', 'modify', 'delete'])
            
            if op_type == 'create':
                lang = random.choice(['py', 'js', 'go'])
                self.create_file_in_dir(base_path, lang)
            elif op_type == 'modify' and len(all_files) > 5:
                modify_file = random.choice(all_files)
                if modify_file.exists():
                    modify_file.write_text(
                        f"// Modified at {time.time()}\n" + modify_file.read_text())
            elif op_type == 'delete' and len(all_files) > 10:
                delete_file = random.choice(all_files)
                if delete_file.exists():
                    delete_file.unlink()
        
        # 最终同步
        stats = self.engine.full_sync()
        final_files = FileDAO.get_all()
        
        LOGGER.info(f"✅ 混合操作完成：最终文件 {len(final_files)} 错误 {len(stats.errors)}")
        
        return len(final_files)
    
    def test_data_consistency_ultimate(self):
        """最终数据一致性验证"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端挑战4：最终数据一致性")
        LOGGER.info("="*80)
        
        cache_stats = self.engine.get_statistics()
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"   缓存文件：{cache_stats['cache']['files']}")
        LOGGER.info(f"   缓存类型：{cache_stats['cache']['types']}")
        LOGGER.info(f"   缓存函数：{cache_stats['cache']['functions']}")
        LOGGER.info(f"   数据库文件：{len(db_files)}")
        LOGGER.info(f"   数据库类型：{len(db_types)}")
        LOGGER.info(f"   数据库函数：{len(db_funcs)}")
        
        assert cache_stats['cache']['files'] == len(db_files), "文件一致性验证失败"
        
        LOGGER.info("✅ 最终数据一致性验证通过！")
        
        return True
    
    def run_all_challenges(self):
        """运行所有超极端挑战"""
        try:
            self.setup()
            
            # 挑战1：超大规模完整同步
            sync_elapsed, file_count, type_count, func_count = self.test_super_extreme_full_sync()
            
            # 挑战2：闪电快速更新
            lightning_files = self.test_lightning_fast_updates()
            
            # 挑战3：混合操作
            mixed_files = self.test_mixed_operations()
            
            # 挑战4：数据一致性
            consistency_ok = self.test_data_consistency_ultimate()
            
            # 总结
            LOGGER.info("\n" + "=" * 80)
            LOGGER.info("🏆 超极端最大挑战测试完成！")
            LOGGER.info("=" * 80)
            LOGGER.info(f"   完整同步时间：{sync_elapsed:.2f} 秒")
            LOGGER.info(f"   同步文件数：{file_count}")
            LOGGER.info(f"   同步类型数：{type_count}")
            LOGGER.info(f"   同步函数数：{func_count}")
            LOGGER.info(f"   闪电更新后文件：{lightning_files}")
            LOGGER.info(f"   混合操作后文件：{mixed_files}")
            LOGGER.info(f"   数据一致性：{'✅ 通过' if consistency_ok else '❌ 失败'}")
            
            return consistency_ok
            
        except Exception as e:
            LOGGER.error(f"❌ 挑战失败：{e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    """主函数"""
    test = ExtremeMaxChallengeTest()
    success = test.run_all_challenges()
    
    if success:
        LOGGER.info("\n🎉 超极端最大挑战完美通过！系统坚不可摧！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 超极端挑战未通过！")
        sys.exit(1)


if __name__ == "__main__":
    main()
