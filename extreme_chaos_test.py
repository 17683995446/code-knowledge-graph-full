#!/usr/bin/env python3
"""
极端混乱场景测试 - 第一次迭代
发现并修复系统真实运行时的 Bug
"""
import os
import sys
import tempfile
import random
import string
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.configuration import LOGGER, set_log_level
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.database.database_connection import DATABASE_CONNECTION
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO

# 设置详细日志
set_log_level('DEBUG')

class ExtremeChaosTest:
    def __init__(self):
        self.test_dir = None
        self.db_path = None
        self.engine = None
        
    def setup(self):
        """设置测试环境"""
        self.test_dir = tempfile.TemporaryDirectory(prefix="extreme_chaos_test_")
        self.db_path = tempfile.mktemp(suffix='.db', prefix='chaos_db_')
        
        # 重新初始化数据库连接
        DATABASE_CONNECTION.initialize(self.db_path, force=True)
        DATABASE_CONNECTION.ensure_tables()
        
        self.engine = IncrementalUpdateEngine(self.test_dir.name)
        LOGGER.info(f"=== 极端混乱测试初始化完成 ===")
        LOGGER.info(f"测试目录: {self.test_dir.name}")
        LOGGER.info(f"数据库: {self.db_path}")
        
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir:
            self.test_dir.cleanup()
        if self.db_path and os.path.exists(self.db_path):
            os.remove(self.db_path)
        LOGGER.info("测试环境清理完成")
        
    def test_find_function_end_bug(self):
        """测试1: 发现 Python 解析器 _find_function_end 方法的严重 Bug"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("📋 测试1: Python 解析器函数结束行 Bug 发现")
        LOGGER.info("="*80)
        
        test_file = Path(self.test_dir.name) / "function_bug_test.py"
        
        # 创建一个有复杂缩进的 Python 文件
        code = '''def buggy_function():
    """这是一个有bug的函数"""
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
        LOGGER.debug(f"创建测试文件: {test_file}")
        
        # 运行引擎
        self.engine.initialize()
        self.engine.full_sync()
        
        # 检查结果
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        functions = FunctionDAO.get_all()
        
        LOGGER.info(f"文件数量: {len(files)}")
        LOGGER.info(f"类型数量: {len(types)}")
        LOGGER.info(f"函数数量: {len(functions)}")
        
        for func in functions:
            LOGGER.info(f"  函数: {func.name}, start={func.start_line}, end={func.end_line}")
        
        # 验证发现的 bug: _find_function_end 返回错误的结束行
        bug_found = False
        for func in functions:
            if func.name == 'buggy_function' and func.end_line < 10:
                LOGGER.error("🚨 BUG 发现! buggy_function 的结束行计算错误!")
                bug_found = True
                
        return bug_found
        
    def create_massive_chaos_project(self, num_files=200):
        """创建极端混乱的大规模项目"""
        LOGGER.info(f"\n📋 创建大规模混乱项目: {num_files} 个文件")
        
        base_dir = Path(self.test_dir.name)
        
        languages = ['py', 'js', 'tsx', 'go', 'java', 'kt', 'ts', 'java']
        file_types = ['normal', 'huge', 'broken', 'unicode', 'binary', 'empty']
        
        for i in range(num_files):
            lang_ext = random.choice(languages)
            file_type = random.choice(file_types)
            
            filename = f"chaos_file_{i:04d}.{lang_ext}"
            filepath = base_dir / filename
            
            if file_type == 'binary':
                # 二进制文件
                filepath.write_bytes(os.urandom(random.randint(100, 2000)))
                
            elif file_type == 'empty':
                # 空文件
                filepath.write_text("")
                
            elif file_type == 'broken':
                # 损坏文件
                if lang_ext == 'py':
                    broken_code = "def broken_func():\n    syntax error here\n    return 1"
                elif lang_ext == 'js':
                    broken_code = "function broken() { \n    invalid syntax \n    return 1 }"
                else:
                    broken_code = "random broken content"
                filepath.write_text(broken_code)
                
            elif file_type == 'unicode':
                # Unicode 文件
                unicode_content = '''def 中文函数():
    """中文文档字符串"""
    class 中文类:
        def 方法(self):
            pass
    return "中文返回值"

class 另一个类:
    def 另一个方法(参数):
        return 参数
'''
                filepath.write_text(unicode_content)
                
            elif file_type == 'huge':
                # 超大文件 (5000+ 行)
                huge_code = []
                for j in range(5000):
                    huge_code.append(f"def func_{j}(x):\n    return x + {j}\n")
                filepath.write_text('\n'.join(huge_code))
                
            else:
                # 正常文件
                self._create_normal_file(filepath, lang_ext, i)
                
        LOGGER.info(f"✅ 完成: 创建了 {num_files} 个混乱文件")
        
    def _create_normal_file(self, filepath, ext, idx):
        """创建正常文件"""
        if ext == 'py':
            code = f'''def func_{idx}(a):
    """Test function {idx}"""
    return a * {idx}

class Class{idx}:
    def method_{idx}(self):
        return "method_{idx}"
'''
        elif ext == 'js':
            code = f'''function func{idx}(x) {{
    return x + {idx};
}}

class Class{idx} {{
    method{idx}() {{
        return "hello";
    }}
}}
'''
        elif ext == 'tsx':
            code = f'''import React from 'react';

interface Props{idx} {{
    name: string;
}}

export function Component{idx}({{ name }}: Props{idx}) {{
    return <div>{{name}}</div>;
}}
'''
        elif ext == 'go':
            code = f'''package main

type Struct{idx} struct {{
    Name string
}}

func (s *Struct{idx}) Method{idx}() string {{
    return "Go {idx}"
}}
'''
        else:
            code = f"// file {idx}"
            
        filepath.write_text(code)
        
    def run_iteration1(self):
        """第一次迭代测试"""
        LOGGER.info("\n" + "="*80)
        LOGGER.info("🚀 第一次迭代: 极端混乱场景测试")
        LOGGER.info("="*80)
        
        self.setup()
        
        try:
            # 测试1: 发现 Python 解析器的 Bug
            bug1_found = self.test_find_function_end_bug()
            
            # 测试2: 大规模混乱项目测试
            LOGGER.info("\n📋 测试2: 大规模混乱项目测试 (200 files)")
            self.create_massive_chaos_project(200)
            self.engine.initialize()
            self.engine.full_sync()
            
            files = FileDAO.get_all()
            types = TypeDAO.get_all()
            functions = FunctionDAO.get_all()
            
            LOGGER.info(f"✅ 大规模同步完成")
            LOGGER.info(f"   - 文件数: {len(files)}")
            LOGGER.info(f"   - 类型数: {len(types)}")
            LOGGER.info(f"   - 函数数: {len(functions)}")
            
            return {
                'bug1_found': bug1_found,
                'files_processed': len(files),
                'types_processed': len(types),
                'functions_processed': len(functions)
            }
            
        except Exception as e:
            LOGGER.error(f"❌ 测试异常: {e}")
            import traceback
            LOGGER.error(traceback.format_exc())
            return {'error': str(e)}
        finally:
            self.cleanup()

def main():
    LOGGER.info("\n" + "="*80)
    LOGGER.info("🔧 极端混乱测试 - 多次迭代发现并修复 Bug")
    LOGGER.info("="*80)
    
    test = ExtremeChaosTest()
    
    # ========== 第一次迭代 ==========
    LOGGER.info("\n" + "="*80)
    LOGGER.info("📌 第一次迭代开始")
    LOGGER.info("="*80)
    
    result1 = test.run_iteration1()
    
    LOGGER.info("\n" + "="*80)
    LOGGER.info("📊 第一次迭代结果")
    LOGGER.info("="*80)
    LOGGER.info(f"结果: {result1}")
    
    if 'bug1_found' in result1 and result1['bug1_found']:
        LOGGER.info("✅ 发现了第一个严重 Bug!")
    else:
        LOGGER.info("❓ 未发现第一个 Bug（可能需要更精确测试）")

if __name__ == "__main__":
    main()
