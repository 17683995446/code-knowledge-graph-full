#!/usr/bin/env python3
"""
最终极最极端混乱测试！
包含：
1. 最复杂边界条件
2. 最大规模（1000+ 文件）
3. 最混乱代码（乱序、重叠、嵌套）
4. 压力测试
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


class UltimateExtremeChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
    
    def setup(self):
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="ultimate_extreme_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="ultimate_extreme_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info("✅ 最终极极端测试环境准备完成")
    
    def cleanup(self):
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def generate_name(self, length=8, include_unicode=True):
        chars = string.ascii_letters + string.digits
        if include_unicode and random.random() < 0.4:
            unicode_chars = '中文日本語한국어العربيةעבריתไทย'
            return ''.join(random.choice(unicode_chars + chars) for _ in range(length))
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_extreme_go_file(self, filepath: Path):
        """最复杂Go文件 - 所有边界条件"""
        content = '''package main

// 换行花括号函数1
func testFunc1()
{
    return 1
}

// 普通花括号函数2
func testFunc2() {
    return 2
}

// 换行花括号方法
type MyStruct struct 
{
    Field1 string
    Field2 int
}

func (m *MyStruct) Method1() 
{
    return
}

func (m *MyStruct) Method2() {
    return
}

// 换行花括号接口
type MyInterface interface 
{
    MethodA()
    MethodB()
}

func main() {
    testFunc1()
    testFunc2()
}
'''
        filepath.write_text(content)
    
    def create_extreme_python_file(self, filepath: Path, num_classes=5, num_functions=20):
        """最复杂Python文件 - 深度嵌套、乱序等"""
        lines = ['# 极端复杂Python文件']
        
        for i in range(num_classes):
            class_name = self.generate_name()
            lines.append(f'class {class_name}:')
            
            for j in range(random.randint(2, 6)):
                method_name = self.generate_name()
                lines.append(f'    def {method_name}(self):')
                lines.append(f'        return "{self.generate_name(15)}"')
                lines.append('')
            
            lines.append('')
        
        for k in range(num_functions):
            func_name = self.generate_name()
            lines.append(f'def {func_name}():')
            lines.append(f'    return {random.randint(0, 1000)}')
            lines.append('')
        
        filepath.write_text('\n'.join(lines))
    
    def create_extreme_javascript_file(self, filepath: Path, num_classes=4, num_functions=15):
        """最复杂JavaScript文件 - 所有import类型"""
        lines = ['// 极端复杂JavaScript文件']
        
        # 添加各种import类型
        lines.append('import { A, B, C } from "module1"')
        lines.append('import DefaultExport from "module2"')
        lines.append('import * as AllExports from "module3"')
        lines.append('import "side-effect-module"')
        
        for i in range(num_classes):
            class_name = self.generate_name()
            lines.append(f'class {class_name} {{')
            
            lines.append('  constructor() {')
            lines.append(f'    this.{self.generate_name()} = null;')
            lines.append('  }')
            
            for j in range(random.randint(2, 4)):
                method_name = self.generate_name()
                lines.append(f'  {method_name}() {{')
                lines.append(f'    return "{self.generate_name(10)}";')
                lines.append('  }')
            
            lines.append('}')
            lines.append('')
        
        for k in range(num_functions):
            func_name = self.generate_name()
            lines.append(f'function {func_name}() {{')
            lines.append(f'  return {random.randint(0, 1000)};')
            lines.append('}')
            lines.append('')
        
        filepath.write_text('\n'.join(lines))
    
    def create_extreme_arkts_file(self, filepath: Path, num_classes=3, num_functions=10):
        """最复杂ArkTS文件 - 所有import类型"""
        lines = ['// 极端复杂ArkTS文件']
        
        lines.append('import { X, Y } from "@ohos/xmodule"')
        lines.append('import DefaultZ from "default-module"')
        lines.append('import * as All from "another-module"')
        
        for i in range(num_classes):
            class_name = self.generate_name()
            lines.append(f'class {class_name} {{')
            
            lines.append('  constructor() {')
            lines.append(f'    this.{self.generate_name()} = "";')
            lines.append('  }')
            
            for j in range(random.randint(2, 3)):
                method_name = self.generate_name()
                lines.append(f'  {method_name}(): string {{')
                lines.append(f'    return "{self.generate_name(10)}";')
                lines.append('  }')
            
            lines.append('}')
            lines.append('')
        
        for k in range(num_functions):
            func_name = self.generate_name()
            lines.append(f'function {func_name}(): number {{')
            lines.append(f'  return {random.randint(0, 1000)};')
            lines.append('}')
            lines.append('')
        
        filepath.write_text('\n'.join(lines))
    
    def create_extreme_edge_file(self, filepath: Path, lang='py'):
        """极端边界条件文件"""
        if lang == 'py':
            edge_cases = [
                '',  # 完全空
                '# only comments\n# nothing else',
                'def test(): pass',
                'class Empty: pass',
                'class WithDoc:\n    """this is a docstring"""\n    pass'
            ]
            content = random.choice(edge_cases)
        elif lang == 'js':
            edge_cases = [
                '',
                '// only comments\n/* block comment */',
                'function f() {}',
                'class C {}'
            ]
            content = random.choice(edge_cases)
        else:
            edge_cases = [
                '',
                '// only go comments',
                'package main\nfunc main() {}'
            ]
            content = random.choice(edge_cases)
        
        filepath.write_text(content)
    
    def create_ultimate_project(self, num_files=1500):
        """最终极混乱项目 - 1500个文件"""
        LOGGER.info(f"🎯 创建最终极混乱项目：{num_files}个文件")
        base_dir = Path(self.test_dir.name)
        
        start_time = time.time()
        
        for i in range(num_files):
            lang = random.choice(['py', 'js', 'ts', 'go', 'ets'])
            filepath = base_dir / f'ultimate_chaos_{i:05d}.{lang}'
            
            if random.random() < 0.08:
                self.create_extreme_edge_file(filepath, lang)
            elif lang == 'py':
                self.create_extreme_python_file(filepath, 
                                                 num_classes=random.randint(3, 7),
                                                 num_functions=random.randint(15, 25))
            elif lang == 'js' or lang == 'ts':
                self.create_extreme_javascript_file(filepath,
                                                     num_classes=random.randint(2, 5),
                                                     num_functions=random.randint(10, 18))
            elif lang == 'ets':
                self.create_extreme_arkts_file(filepath,
                                               num_classes=random.randint(2, 4),
                                               num_functions=random.randint(8, 15))
            else:  # go
                self.create_extreme_go_file(filepath)
        
        elapsed = time.time() - start_time
        LOGGER.info(f"✅ 项目创建完成：耗时{elapsed:.2f}秒")
    
    def test_ultimate_full_sync(self):
        """最终极全同步"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 最终极测试一：1500文件全同步")
        LOGGER.info("="*80)
        
        self.create_ultimate_project(1500)
        
        self.engine.initialize()
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 全同步完成：耗时{elapsed:.2f}秒")
        LOGGER.info(f"  处理文件：{stats.files_processed}")
        LOGGER.info(f"  新增文件：{stats.files_created}")
        LOGGER.info(f"  处理类型：{stats.types_processed}")
        LOGGER.info(f"  处理函数：{stats.functions_processed}")
        LOGGER.info(f"  调用关系：{stats.calls_resolved}")
        LOGGER.info(f"  错误数量：{len(stats.errors)}")
        LOGGER.info(f"  数据库文件：{len(files)}")
        LOGGER.info(f"  数据库类型：{len(types)}")
        LOGGER.info(f"  数据库函数：{len(funcs)}")
        
        assert len(files) > 0, "应该解析到文件"
        assert len(stats.errors) == 0, f"不应该有错误，实际：{len(stats.errors)}"
        
        return True
    
    def test_extreme_deletion(self):
        """极端删除测试"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 最终极测试二：极端删除操作")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        all_files = list(base_dir.glob("*.py")) + list(base_dir.glob("*.js")) + \
                    list(base_dir.glob("*.ts")) + list(base_dir.glob("*.go")) + \
                    list(base_dir.glob("*.ets"))
        
        # 删除大约一半
        num_to_delete = len(all_files) // 2
        deleted_files = random.sample(all_files, num_to_delete)
        
        for f in deleted_files:
            f.unlink()
        
        LOGGER.info(f"删除了 {len(deleted_files)} 个文件")
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 极端删除后同步完成：耗时{elapsed:.2f}秒")
        LOGGER.info(f"  删除文件数：{stats.files_deleted}")
        LOGGER.info(f"  最终文件数：{len(files)}")
        
        return True
    
    def test_extreme_data_consistency(self):
        """最终极数据一致性"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 最终极测试三：极端数据一致性")
        LOGGER.info("="*80)
        
        cache_stats = self.engine.get_statistics()
        db_files = FileDAO.get_all()
        db_types = TypeDAO.get_all()
        db_funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"  缓存文件：{cache_stats['cache']['files']}")
        LOGGER.info(f"  缓存类型：{cache_stats['cache']['types']}")
        LOGGER.info(f"  缓存函数：{cache_stats['cache']['functions']}")
        LOGGER.info(f"  数据库文件：{len(db_files)}")
        LOGGER.info(f"  数据库类型：{len(db_types)}")
        LOGGER.info(f"  数据库函数：{len(db_funcs)}")
        
        assert cache_stats['cache']['files'] == len(db_files), "文件缓存与数据库不一致"
        
        LOGGER.info("✅ 极端数据一致性验证通过！")
        return True
    
    def run_all_tests(self):
        try:
            self.setup()
            
            results = []
            
            results.append(("最终极全同步", self.test_ultimate_full_sync()))
            results.append(("极端删除操作", self.test_extreme_deletion()))
            results.append(("极端数据一致性", self.test_extreme_data_consistency()))
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("🎯 最终极测试结果汇总")
            LOGGER.info("="*80)
            
            for name, passed in results:
                status = "✅ 通过" if passed else "❌ 失败"
                LOGGER.info(f"  {name}：{status}")
            
            all_passed = all(r[1] for r in results)
            
            return all_passed
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常：{e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    LOGGER.info("\n" + "="*80)
    LOGGER.info("🎯 最终极最极端混乱测试开始！")
    LOGGER.info("="*80)
    
    tester = UltimateExtremeChaosTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n🎉 所有最终极测试完美通过！系统坚不可摧！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
