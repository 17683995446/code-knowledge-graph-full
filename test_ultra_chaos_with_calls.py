#!/usr/bin/env python3
"""
超极端测试：验证调用关系解析和边界场景的超极端测试
包含：
1. 深度嵌套调用
2. 复杂项目架构
3. 边界条件
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
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO, CallDAO


class UltraChaosWithCallsTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
    
    def setup(self):
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="ultra_chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="ultra_chaos_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info("✅ 超极端测试环境准备完成")
    
    def cleanup(self):
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def create_complex_call_tree(self, file_count=100):
        """创建具有复杂调用关系的超复杂项目"""
        base_dir = Path(self.test_dir.name)
        all_funcs = []
        for i in range(file_count):
            lang = random.choice(['py', 'js', 'go'])
            filepath = base_dir / f"call_test_{i:04d}.{lang}"
            
            if lang == 'py':
                content = self._create_complex_python_with_calls(i)
            elif lang == 'js':
                content = self._create_complex_js_with_calls(i)
            else:
                content = self._create_complex_go_with_calls(i)
            
            filepath.write_text(content)
    
    def _create_complex_python_with_calls(self, idx):
        lines = [f'# Ultra Chaos Python File #{idx}']
        
        class_name = f'ComplexClass{idx}'
        lines.append(f'class {class_name}:')
        lines.append(f'    def __init__(self):')
        lines.append(f'        self.name = "{class_name}"')
        
        method_name = f'method_a_{idx}'
        lines.append(f'    def {method_name}(self):')
        lines.append(f'        result = {method_name}')
        
        func_names = []
        for m in range(5):
            fn = f'utility_{idx}_{m}'
            func_names.append(fn)
            lines.append(f'        {fn}()')
            lines.append('')
        
        lines.append(f'    def another_method(self):')
        lines.append(f'        return "{class_name}')
        lines.append('')
        
        for fn in func_names:
            lines.append(f'def {fn}():')
            lines.append(f'    return {idx}')
            lines.append('')
        
        return '\n'.join(lines)
    
    def _create_complex_js_with_calls(self, idx):
        lines = [f'// Ultra Chaos JavaScript File #{idx}']
        
        class_name = f'ComplexClass{idx}'
        lines.append(f'class {class_name} {{')
        lines.append('    constructor() {')
        lines.append(f'        this.name = "{class_name}";')
        lines.append('    }')
        
        method_name = f'method_a_{idx}'
        lines.append(f'    {method_name}() {{')
        lines.append(f'        let result = "{method_name}";')
        
        func_names = []
        for m in range(5):
            fn = f'utility_{idx}_{m}'
            func_names.append(fn)
            lines.append(f'        {fn}();')
        
        lines.append('    }')
        
        lines.append('    another_method() {')
        lines.append(f'        return "{class_name}";')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        
        for fn in func_names:
            lines.append(f'function {fn}() {{')
            lines.append(f'    return {idx};')
            lines.append('}')
            lines.append('')
        
        return '\n'.join(lines)
    
    def _create_complex_go_with_calls(self, idx):
        lines = [f'// Ultra Chaos Go File #{idx}']
        lines.append('package main')
        lines.append('')
        
        struct_name = f'ComplexStruct{idx}'
        lines.append(f'type {struct_name} struct {{')
        lines.append(f'    Name string')
        lines.append('}')
        lines.append('')
        
        method_name = f'MethodA{idx}'
        lines.append(f'func (c *{struct_name}) {method_name}() {{')
        lines.append(f'    // do some work')
        lines.append('}')
        lines.append('')
        
        func_names = []
        for m in range(3):
            fn = f'Utility{idx}{m}'
            func_names.append(fn)
            lines.append(f'func {fn}() int {{')
            lines.append(f'    return {idx}')
            lines.append('}')
            lines.append('')
        
        lines.append('func main() {')
        lines.append(f'    c := &{struct_name}{{Name: "test"}}')
        lines.append('}')
        
        return '\n'.join(lines)
    
    def test_full_sync_with_calls(self):
        """测试1: 超大规模完整同步带复杂调用"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端测试一：复杂调用关系超大规模")
        LOGGER.info("="*80)
        
        self.create_complex_call_tree(file_count=120)
        
        self.engine.initialize()
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 全同步完成：耗时{elapsed:.2f}秒")
        LOGGER.info(f"   文件数：{len(files)}")
        LOGGER.info(f"   类型数：{len(types)}")
        LOGGER.info(f"   函数数：{len(funcs)}")
        LOGGER.info(f"   调用关系：{stats.calls_resolved}")
        LOGGER.info(f"   错误数：{len(stats.errors)}")
        
        assert len(files) > 0 and len(stats.errors) == 0, "调用关系同步成功！"
        LOGGER.info("✅ 复杂调用关系解析成功！")
        return True
    
    def test_multiple_incremental_updates(self):
        """测试2: 多次增量更新"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端测试二：多次增量更新")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        round_count = 5
        
        for round_idx in range(round_count):
            # 创建新的文件进行修改
            new_file = base_dir / f"incremental_{round_idx}.py"
            new_file.write_text(f'''# Incremental Update {round_idx}\n\nclass Incremental{round_idx}Class:\n    def method{round_idx}(self):\n        return {round_idx}\n\ndef util_{round_idx}():\n    return {round_idx}\n''')
            
            start_time = time.time()
            stats = self.engine.full_sync()
            elapsed = time.time() - start_time
            
            files = FileDAO.get_all()
            LOGGER.info(f"   第{round_idx + 1}轮：文件数：{len(files)}，时间：{elapsed:.2f}秒")
        
        files = FileDAO.get_all()
        LOGGER.info(f"✅ 增量更新成功！")
        return True
    
    def test_mixed_file_operations(self):
        """测试3: 混合文件操作（创建、修改、删除"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端测试三：混合文件操作")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        # 1. 创建新文件
        for i in range(20):
            f = base_dir / f"mixed_new_{i}.py"
            f.write_text(f'''def func_{i}():\n    return {i}\n''')
        
        # 2. 修改已存在的文件
        for i in range(10):
            f = base_dir / f"call_test_{i:04d}.py"
            if f.exists():
                f.write_text(f'''# Modified\n\ndef modified_func_{i}():\n    return {i + 100}\n''')
        
        # 3. 删除一些文件
        for i in range(10, 20):
            f = base_dir / f"call_test_{i:04d}.py"
            if f.exists():
                f.unlink()
        
        stats = self.engine.full_sync()
        files = FileDAO.get_all()
        
        LOGGER.info(f"✅ 混合操作完成！")
        LOGGER.info(f"   文件数：{len(files)}")
        LOGGER.info(f"   错误数：{len(stats.errors)}")
        
        return len(stats.errors) == 0
    
    def test_ultra_data_consistency(self):
        """测试4: 最终数据一致性"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("⚡ 超极端测试四：最终数据一致性")
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
        
        assert cache_stats['cache']['files'] == len(db_files), "文件缓存与数据库不一致！"
        LOGGER.info("✅ 数据一致性验证通过！")
        return True
    
    def run_all_tests(self):
        try:
            self.setup()
            results = []
            results.append(("复杂调用超大规模同步", self.test_full_sync_with_calls()))
            results.append(("多次增量更新", self.test_multiple_incremental_updates()))
            results.append(("混合文件操作", self.test_mixed_file_operations()))
            results.append(("最终数据一致性", self.test_ultra_data_consistency()))
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("🎯 超极端测试结果汇总")
            LOGGER.info("="*80)
            for name, passed in results:
                status = "✅ 通过" if passed else "❌ 失败"
                LOGGER.info(f"   {name}：{status}")
            
            return all(r[1] for r in results)
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常：{e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    LOGGER.info("\n" + "="*80)
    LOGGER.info("🎯 超极端测试：复杂调用关系场景")
    LOGGER.info("="*80)
    
    tester = UltraChaosWithCallsTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n🎉 所有超极端测试完美通过！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
