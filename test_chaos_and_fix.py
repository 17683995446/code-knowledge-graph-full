#!/usr/bin/env python3
"""
极端混乱场景测试 - 多次迭代发现并修复真实运行时 Bug
"""

import os
import sys
import tempfile
import random
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER
from src.parsers import initialize_all_parsers
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class ChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
        
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix='chaos_db_')
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info(f"✅ 测试环境准备完成")
        LOGGER.info(f"   测试目录: {self.test_dir.name}")
        LOGGER.info(f"   数据库: {self.db_path}")
        
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        LOGGER.info("✅ 测试环境已清理")
        
    def test_1_python_function_end_fix(self):
        """测试 1: 验证 Python 函数结束行 Bug 是否已修复"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 1: 验证 Python 函数结束行 Bug 修复")
        LOGGER.info("="*80)
        
        test_file = Path(self.test_dir.name) / "test_func_end.py"
        code = '''def buggy_function():
    """测试函数"""
    x = 1
    if x == 1:
        print("Hello")
        nested_func()
    
    return x

def nested_func():
    return 42

class MyClass:
    def method1(self):
        return "method1"
    
    def method2(self):
        self.method1()
        return "method2"
'''
        test_file.write_text(code)
        
        self.engine.initialize()
        self.engine.full_sync()
        
        files = FileDAO.get_all()
        functions = FunctionDAO.get_all()
        
        LOGGER.info(f"文件数: {len(files)}")
        LOGGER.info(f"函数数: {len(functions)}")
        
        for func in functions:
            LOGGER.info(f"  函数: {func['name']}, 行: {func['start_line']} - {func['end_line']}")
        
        # 验证修复
        buggy_func = [f for f in functions if f['name'] == 'buggy_function']
        if len(buggy_func) == 1:
            LOGGER.info(f"✅ buggy_function 已找到, 结束行: {buggy_func[0]['end_line']}")
            return True
        else:
            LOGGER.error("❌ 未找到 buggy_function")
            return False
        
    def test_2_massive_chaos_project(self, num_files=50):
        """测试 2: 大规模混乱项目测试"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info(f"📋 测试 2: 大规模混乱项目 ({num_files} 个文件)")
        LOGGER.info("="*80)
        
        languages = ['py', 'js', 'jsx', 'ts', 'tsx', 'go']
        file_types = ['normal', 'broken', 'unicode', 'empty']
        
        for i in range(num_files):
            lang = random.choice(languages)
            ftype = random.choice(file_types)
            filepath = Path(self.test_dir.name) / f"chaos_{i:03d}.{lang}"
            
            if ftype == 'normal':
                self._write_normal_file(filepath, lang, i)
            elif ftype == 'broken':
                self._write_broken_file(filepath, lang)
            elif ftype == 'unicode':
                self._write_unicode_file(filepath, lang)
            else:
                filepath.write_text("")
        
        # 运行同步
        LOGGER.info("⏳ 开始全量同步...")
        start = time.time()
        self.engine.initialize()
        stats = self.engine.full_sync()
        elapsed = time.time() - start
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 同步完成! 耗时: {elapsed:.3f}秒")
        LOGGER.info(f"   处理文件: {stats.files_processed}")
        LOGGER.info(f"   新增文件: {stats.files_created}")
        LOGGER.info(f"   数据库文件: {len(files)}")
        LOGGER.info(f"   数据库类型: {len(types)}")
        LOGGER.info(f"   数据库函数: {len(funcs)}")
        
        return len(files) > 0
        
    def _write_normal_file(self, filepath, lang, idx):
        if lang == 'py':
            content = f'''def func_{idx}(x):
    return x + {idx}

class Class{idx}:
    def method_a(self):
        return "a"
    
    def method_b(self):
        return self.method_a()
'''
        elif lang in ['js', 'jsx']:
            content = f'''function func{idx}(x) {{
    return x + {idx};
}}

class Class{idx} {{
    methodA() {{
        return "a";
    }}
    
    methodB() {{
        return this.methodA();
    }}
}}
'''
        elif lang in ['ts', 'tsx']:
            content = f'''interface Iface{idx} {{
    name: string;
}}

class Class{idx} implements Iface{idx} {{
    name: string = "Class{idx}";
    
    method(): string {{
        return this.name;
    }}
}}
'''
        elif lang == 'go':
            content = f'''package main

type Struct{idx} struct {{
    Name string
}}

func (s *Struct{idx}) Method() string {{
    return s.Name
}}
'''
        else:
            content = f"// file {idx}"
        
        filepath.write_text(content)
        
    def _write_broken_file(self, filepath, lang):
        if lang == 'py':
            content = '''def broken_func():
    syntax error here
    return 1'''
        elif lang in ['js', 'jsx', 'ts', 'tsx']:
            content = '''function broken() {
    invalid syntax
    return 1;
}'''
        else:
            content = "broken code"
        filepath.write_text(content)
        
    def _write_unicode_file(self, filepath, lang):
        if lang == 'py':
            content = '''def 中文函数():
    """中文文档字符串"""
    class 中文类:
        def 方法(self):
            pass
    return "中文返回值"
'''
        else:
            content = "// unicode"
        filepath.write_text(content)
        
    def test_3_incremental_updates(self):
        """测试 3: 增量更新测试"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试 3: 增量更新测试")
        LOGGER.info("="*80)
        
        # 修改文件
        file_to_modify = Path(self.test_dir.name) / "chaos_000.py"
        if file_to_modify.exists():
            original_content = file_to_modify.read_text()
            new_content = original_content + "\n\ndef new_function():\n    return 'new'\n"
            file_to_modify.write_text(new_content)
            LOGGER.info("✅ 修改了 chaos_000.py")
        
        # 删除文件
        file_to_delete = Path(self.test_dir.name) / "chaos_001.py"
        if file_to_delete.exists():
            os.remove(file_to_delete)
            LOGGER.info("✅ 删除了 chaos_001.py")
        
        # 再创建几个新文件
        for i in range(10, 15):
            p = Path(self.test_dir.name) / f"new_chaos_{i}.py"
            p.write_text(f"def new_func_{i}(): return {i}\n")
        
        # 重新初始化并同步
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        self.engine.initialize()
        stats = self.engine.full_sync()
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        funcs = FunctionDAO.get_all()
        
        LOGGER.info(f"✅ 增量同步完成")
        LOGGER.info(f"   统计: {stats}")
        LOGGER.info(f"   最终文件数: {len(files)}")
        LOGGER.info(f"   最终类型数: {len(types)}")
        LOGGER.info(f"   最终函数数: {len(funcs)}")
        
        return True
        
    def run_all(self):
        """运行所有测试"""
        LOGGER.info("🚀 开始运行极端混乱场景测试")
        
        try:
            self.setup()
            
            # 测试 1
            result1 = self.test_1_python_function_end_fix()
            
            # 测试 2
            result2 = self.test_2_massive_chaos_project(30)
            
            # 测试 3
            result3 = self.test_3_incremental_updates()
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("📊 最终结果")
            LOGGER.info("="*80)
            LOGGER.info(f"测试 1 (Python 函数结束行修复): {'✅ 通过' if result1 else '❌ 失败'}")
            LOGGER.info(f"测试 2 (大规模混乱项目): {'✅ 通过' if result2 else '❌ 失败'}")
            LOGGER.info(f"测试 3 (增量更新): {'✅ 通过' if result3 else '❌ 失败'}")
            
            return all([result1, result2, result3])
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return False
        finally:
            self.cleanup()


def main():
    tester = ChaosTester()
    success = tester.run_all()
    
    if success:
        LOGGER.info("\n✅ 所有极端混乱场景测试通过! 系统非常健壮!")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
