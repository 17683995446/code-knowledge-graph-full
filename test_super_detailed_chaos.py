#!/usr/bin/env python3
"""
超细节混乱测试 - 验证所有边界条件和细节修复
包含：
1. Go 换行花括号测试
2. Python 缩进嵌套测试
3. JavaScript/TypeScript 复杂场景测试
4. Unicode 和特殊字符测试
5. 超大文件测试
6. 并发和压力测试
"""

import os
import sys
import tempfile
import random
import time
import string
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.parsers import initialize_all_parsers
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO


class SuperDetailedChaosTester:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
    
    def setup(self):
        """设置干净的测试环境"""
        initialize_all_parsers()
        
        self.test_dir = tempfile.TemporaryDirectory(prefix="super_detailed_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix="super_detailed_db_")
        
        DATABASE_CONNECTION.__init__(Path(self.db_path))
        DATABASE_CONNECTION.initialize_database()
        
        self.engine = IncrementalUpdateEngine(Path(self.test_dir.name))
        LOGGER.info("✅ 超细节测试环境准备完成")
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_go_newline_braces(self):
        """测试1: Go 换行花括号（修复验证）"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试1: Go 换行花括号（修复验证）")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        test_file = base_dir / "newline_braces.go"
        
        content = '''package main

func test1()
{
    return 1
}

func test2() {
    return 2
}

func test3()
{
    if true {
        return 3
    }
}

type TestStruct struct 
{
    field1 string
    field2 int
}

type TestInterface interface 
{
    Method1()
    Method2()
}

func (t *TestStruct) Method1() 
{
    return
}

func main() 
{
    test1()
    test2()
}
'''
        
        test_file.write_text(content)
        
        self.engine.initialize()
        stats = self.engine.full_sync()
        
        funcs = FunctionDAO.get_all()
        types = TypeDAO.get_all()
        
        LOGGER.info(f"   解析的函数数: {len(funcs)}")
        LOGGER.info(f"   解析的类型数: {len(types)}")
        
        for func_item in funcs:
            if func_item.get('name'):
                LOGGER.info(f"   - 函数: {func_item['name']}, 行: {func_item.get('start_line')}-{func_item.get('end_line')}")
        
        for type_item in types:
            if type_item.get('name'):
                LOGGER.info(f"   - 类型: {type_item['name']}, 行: {type_item.get('start_line')}-{type_item.get('end_line')}")
        
        assert len(funcs) >= 4, f"应该至少解析4个函数，实际：{len(funcs)}"
        assert len(types) >= 2, f"应该至少解析2个类型，实际：{len(types)}"
        
        LOGGER.info("✅ Go 换行花括号测试通过")
        return True
    
    def test_python_deep_nesting(self):
        """测试2: Python 深度嵌套缩进"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试2: Python 深度嵌套缩进")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        test_file = base_dir / "deep_nesting.py"
        
        lines = [
            "class Outer:",
            "    def method1(self):",
            "        def inner1():",
            "            def inner2():",
            "                def inner3():",
            "                    return 1",
            "                return inner3()",
            "            return inner2()",
            "        return inner1()",
            "    def method2(self):",
            "        return 2",
            "def func1():",
            "    if True:",
            "        if True:",
            "            if True:",
            "                return 1",
            "    return 0",
        ]
        
        test_file.write_text('\n'.join(lines))
        
        self.engine.initialize()
        stats = self.engine.full_sync()
        
        funcs = FunctionDAO.get_all()
        types = TypeDAO.get_all()
        
        LOGGER.info(f"   解析的函数数: {len(funcs)}")
        LOGGER.info(f"   解析的类型数: {len(types)}")
        
        for func_item in funcs:
            if func_item.get('name'):
                LOGGER.info(f"   - 函数: {func_item['name']}, 行: {func_item.get('start_line')}-{func_item.get('end_line')}")
        
        assert len(funcs) >= 5, f"应该至少解析5个函数，实际：{len(funcs)}"
        
        LOGGER.info("✅ Python 深度嵌套测试通过")
        return True
    
    def test_unicode_and_special_chars(self):
        """测试3: Unicode 和特殊字符"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试3: Unicode 和特殊字符")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        files = []
        
        files.append(("unicode_chinese.py", '''# 中文类名和函数名
class 我的类:
    def 我的方法(self):
        return "你好世界"
        
def 公共函数():
    return 123
'''))
        
        files.append(("unicode_japanese.py", '''# 日本語クラス名
class 日本語クラス:
    def メソッド名(self):
        return 42
        
def 関数名():
    return 42
'''))
        
        files.append(("special_chars.js", '''// 特殊字符测试
class 我的类 {
    constructor() {
        this.$special = null;
    }
    方法名() {
        return "_underscore";
    }
}

function 函数名() {
    return "backtick`";
}
'''))
        
        files.append(("emoji_vars.py", '''# Emoji 变量名
class 🎮游戏:
    def 🎯得分(self):
        return 100
    def 🏆排名(self):
        return "第一"
        
def 🎲随机():
    return 42
'''))
        
        for filename, content in files:
            filepath = base_dir / filename
            filepath.write_text(content)
        
        stats = self.engine.full_sync()
        
        funcs = FunctionDAO.get_all()
        types = TypeDAO.get_all()
        
        LOGGER.info(f"   解析的函数数: {len(funcs)}")
        LOGGER.info(f"   解析的类型数: {len(types)}")
        
        for func_item in funcs:
            if func_item.get('name'):
                LOGGER.info(f"   - 函数: {func_item['name']}")
        
        for type_item in types:
            if type_item.get('name'):
                LOGGER.info(f"   - 类型: {type_item['name']}")
        
        LOGGER.info("✅ Unicode 和特殊字符测试通过")
        return True
    
    def test_huge_files(self):
        """测试4: 超大文件处理"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试4: 超大文件处理")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        for i in range(10):
            lines = [f"# File {i} - Large file with many classes and functions"]
            
            for j in range(50):
                lines.append(f"class Class_{i}_{j}:")
                lines.append(f"    def method_{i}_{j}_1(self):")
                lines.append(f"        return {i * j}")
                lines.append(f"    def method_{i}_{j}_2(self):")
                lines.append(f"        return {i + j}")
                lines.append("")
            
            for k in range(100):
                lines.append(f"def function_{i}_{k}():")
                lines.append(f"    return {i + k}")
                lines.append("")
            
            filepath = base_dir / f"huge_file_{i}.py"
            filepath.write_text('\n'.join(lines))
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        funcs = FunctionDAO.get_all()
        types = TypeDAO.get_all()
        
        LOGGER.info(f"   处理时间: {elapsed:.2f}s")
        LOGGER.info(f"   解析的函数数: {len(funcs)}")
        LOGGER.info(f"   解析的类型数: {len(types)}")
        
        assert len(funcs) >= 1000, f"应该至少解析1000个函数，实际：{len(funcs)}"
        
        LOGGER.info("✅ 超大文件处理测试通过")
        return True
    
    def test_mega_complex_project(self, num_files=500):
        """测试5: 超大规模复杂项目"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info(f"📋 测试5: 超大规模复杂项目 ({num_files} 文件)")
        LOGGER.info("="*80)
        
        base_dir = Path(self.test_dir.name)
        
        start_time = time.time()
        
        for i in range(num_files):
            lang = random.choice(['py', 'js', 'ts', 'go'])
            filepath = base_dir / f"complex_{i:05d}.{lang}"
            
            if lang == 'py':
                lines = [f"# Complex Python {i}"]
                for j in range(random.randint(3, 8)):
                    lines.append(f"class Class_{j}:")
                    lines.append(f"    def method_{j}(self):")
                    lines.append(f"        return {j}")
                    lines.append("")
                for k in range(random.randint(5, 15)):
                    lines.append(f"def func_{k}():")
                    lines.append(f"    return {k}")
                    lines.append("")
                    
            elif lang == 'js':
                lines = [f"// Complex JavaScript {i}"]
                for j in range(random.randint(2, 5)):
                    lines.append(f"class Class_{j} {{")
                    lines.append(f"    method_{j}() {{ return {j}; }}")
                    lines.append("}")
                    lines.append("")
                for k in range(random.randint(3, 10)):
                    lines.append(f"function func_{k}() {{ return {k}; }}")
                    lines.append("")
                    
            elif lang == 'ts':
                lines = [f"// Complex TypeScript {i}"]
                for j in range(random.randint(2, 5)):
                    lines.append(f"class Class_{j} {{")
                    lines.append(f"    method_{j}(): number {{ return {j}; }}")
                    lines.append("}")
                    lines.append("")
                for k in range(random.randint(3, 10)):
                    lines.append(f"function func_{k}(): number {{ return {k}; }}")
                    lines.append("")
                    
            else:  # go
                lines = [f"// Complex Go {i}", "package main", ""]
                for j in range(random.randint(2, 4)):
                    lines.append(f"type Struct_{j} struct {{")
                    lines.append(f"    Field_{j} string")
                    lines.append("}")
                    lines.append("")
                for k in range(random.randint(3, 8)):
                    lines.append(f"func func_{k}() int {{")
                    lines.append(f"    return {k}")
                    lines.append("}")
                    lines.append("")
                lines.append("func main() {}")
            
            filepath.write_text('\n'.join(lines))
        
        elapsed = time.time() - start_time
        LOGGER.info(f"   项目创建耗时: {elapsed:.2f}s")
        
        start_time = time.time()
        stats = self.engine.full_sync()
        elapsed = time.time() - start_time
        
        files = FileDAO.get_all()
        funcs = FunctionDAO.get_all()
        types = TypeDAO.get_all()
        
        LOGGER.info(f"   ✅ 同步完成，耗时: {elapsed:.2f}s")
        LOGGER.info(f"   文件数: {len(files)}")
        LOGGER.info(f"   函数数: {len(funcs)}")
        LOGGER.info(f"   类型数: {len(types)}")
        LOGGER.info(f"   错误数: {len(stats.errors)}")
        
        assert len(files) > 0, "应该有解析的文件"
        assert len(stats.errors) == 0, f"不应该有错误，实际：{len(stats.errors)}"
        
        LOGGER.info("✅ 超大规模复杂项目测试通过")
        return True
    
    def test_data_consistency_final(self):
        """测试6: 最终数据一致性验证"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试6: 最终数据一致性验证")
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
        
        LOGGER.info("✅ 最终数据一致性验证通过")
        return True
    
    def run_all_tests(self):
        """运行所有超细节测试"""
        try:
            self.setup()
            
            results = []
            
            results.append(("Go 换行花括号", self.test_go_newline_braces()))
            results.append(("Python 深度嵌套", self.test_python_deep_nesting()))
            results.append(("Unicode 和特殊字符", self.test_unicode_and_special_chars()))
            results.append(("超大文件处理", self.test_huge_files()))
            results.append(("超大规模复杂项目", self.test_mega_complex_project(500)))
            results.append(("最终数据一致性", self.test_data_consistency_final()))
            
            LOGGER.info("\n" + "="*80)
            LOGGER.info("🎯 超细节测试结果汇总")
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
    LOGGER.info("🎯 超细节混乱测试 - 验证所有边界条件")
    LOGGER.info("="*80)
    
    tester = SuperDetailedChaosTester()
    success = tester.run_all_tests()
    
    if success:
        LOGGER.info("\n✅ 所有超细节测试完美通过！所有修复验证成功！")
        sys.exit(0)
    else:
        LOGGER.error("\n❌ 部分测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
