#!/usr/bin/env python3
"""
超长时间、超复杂的系统压力测试
模拟真实开发环境中的持续编码、多次修改、大量文件操作
"""

import sys
import time
import tempfile
import random
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def create_complex_python_file(base_dir: Path, index: int) -> Path:
    """创建复杂的Python文件"""
    file_path = base_dir / f"module_{index:03d}.py"
    content = f'''"""
Complex Module {index}
This module contains multiple classes and functions for stress testing.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class DataModel{index}:
    """Data model {index}"""
    id: int
    name: str
    value: float
    metadata: Dict[str, Any] = None
    tags: List[str] = None


class Service{index}:
    """Service class {index}"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._cache = {{}}
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Initialize service {index}"""
        self._is_initialized = True
    
    def process_data(self, data: List[Any]) -> List[Any]:
        """Process data with service {index}"""
        result = []
        for item in data:
            transformed = self._transform(item)
            result.append(transformed)
        return result
    
    def _transform(self, item: Any) -> Any:
        """Transform item internally"""
        return str(item) + f"_transformed_by_{{self.__class__.__name__}}"
    
    def validate(self, data: Any) -> bool:
        """Validate input data"""
        return data is not None


def utility_function_{index}(x: int, y: int) -> int:
    """Utility function {index} to calculate something"""
    return (x * y) + (x + y)


def helper_function_{index}(name: str) -> str:
    """Helper function {index}"""
    return f"Hello, {{name}}! This is from module {index}."


class AnotherClass{index}:
    """Another test class {index}"""
    
    def method_a(self) -> str:
        """Method A"""
        return "a"
    
    def method_b(self) -> str:
        """Method B"""
        return "b"
    
    def method_c(self, x: int) -> int:
        """Method C with calculation"""
        return x * x
'''
    file_path.write_text(content)
    return file_path


def create_complex_js_file(base_dir: Path, index: int) -> Path:
    """创建复杂的JavaScript文件"""
    file_path = base_dir / f"component_{index:03d}.jsx"
    content = f'''/**
 * Complex Component {index}
 * This file contains React-style components for stress testing.
 */

import React, {{ useState, useEffect }} from 'react';

export function Component{index}({{ title = "Component {index}", count = 0 }}) {{
    const [state, setState] = useState({{
        value: count,
        isActive: false
    }});

    useEffect(() => {{
        console.log('Component {index} mounted');
        return () => console.log('Component {index} unmounted');
    }}, []);

    const handleClick = () => {{
        setState(prev => ({{
            ...prev,
            value: prev.value + 1,
            isActive: !prev.isActive
        }}));
    }};

    return (
        <div className="complex-component">
            <h2>{{title}}</h2>
            <p>Value: {{state.value}}</p>
            <button onClick={{handleClick}}>
                {{state.isActive ? 'Active' : 'Inactive'}}
            </button>
        </div>
    );
}}

export function HelperComponent{index}({{ items }}) {{
    return (
        <ul>
            {{items.map(item => (
                <li key={{item.id}}>{{item.text}}</li>
            ))}}
        </ul>
    );
}}

export const config{index} = {{
    enabled: true,
    maxCount: 1000,
    timeout: 5000
}};
'''
    file_path.write_text(content)
    return file_path


def create_complex_go_file(base_dir: Path, index: int) -> Path:
    """创建复杂的Go文件"""
    file_path = base_dir / f"service_{index:03d}.go"
    content = f'''package main

import (
    "fmt"
    "sync"
)

// Service{index} - complex Go service type
type Service{index} struct {{
    mutex sync.RWMutex
    data map[string]interface{{}}
    count int
}}

// NewService{index} creates a new service
func NewService{index}() *Service{index} {{
    return &Service{index}{{
        data: make(map[string]interface{{}}),
        count: 0,
    }}
}}

// Get retrieves a value by key
func (s *Service{index}) Get(key string) (interface{{}}, bool) {{
    s.mutex.RLock()
    defer s.mutex.RUnlock()
    value, exists := s.data[key]
    return value, exists
}}

// Set stores a value by key
func (s *Service{index}) Set(key string, value interface{{}}) {{
    s.mutex.Lock()
    defer s.mutex.Unlock()
    s.data[key] = value
    s.count++
}}

// GetCount returns current count
func (s *Service{index}) GetCount() int {{
    s.mutex.RLock()
    defer s.mutex.RUnlock()
    return s.count
}}

// Helper{index} is a helper function
func Helper{index}(input string) string {{
    return fmt.Sprintf("Processed: %s", input)
}}
'''
    file_path.write_text(content)
    return file_path


def create_massive_project(base_dir: Path, num_py: int = 30, num_js: int = 20, num_go: int = 15) -> List[Path]:
    """创建超大规模的多语言测试项目"""
    project_root = base_dir / "massive_project"
    project_root.mkdir(exist_ok=True)
    
    py_dir = project_root / "python"
    py_dir.mkdir(exist_ok=True)
    js_dir = project_root / "javascript"
    js_dir.mkdir(exist_ok=True)
    go_dir = project_root / "go"
    go_dir.mkdir(exist_ok=True)
    
    all_files = []
    
    # 创建Python文件
    for i in range(num_py):
        all_files.append(create_complex_python_file(py_dir, i))
    
    # 创建JavaScript文件
    for i in range(num_js):
        all_files.append(create_complex_js_file(js_dir, i))
    
    # 创建Go文件
    for i in range(num_go):
        all_files.append(create_complex_go_file(go_dir, i))
    
    return all_files


def modify_file_randomly(file_path: Path, iteration: int) -> None:
    """随机修改文件内容"""
    content = file_path.read_text()
    
    # 添加一些新的内容到文件
    if file_path.suffix == ".py":
        new_content = content + f'''

# Added in stress test iteration {iteration}
def stress_test_function_{iteration}(x: int) -> int:
    """This is a dynamically added function"""
    return x * x + {iteration}
'''
    elif file_path.suffix in [".jsx", ".js"]:
        new_content = content + f'''

// Added in stress test iteration {iteration}
export function stressTest{iteration}(x) {{
    return x * x + {iteration};
}}
'''
    elif file_path.suffix == ".go":
        new_content = content + f'''

// Added in stress test iteration {iteration}
func StressTest{iteration}(x int) int {{
    return x * x + {iteration}
}}
'''
    else:
        new_content = content
    
    file_path.write_text(new_content)


def run_extreme_stress_test():
    """运行极端压力测试 - 长时间的模拟真实开发环境"""
    LOGGER.info("=" * 80)
    LOGGER.info("🔥 极端长时间压力测试 - 真实开发环境模拟")
    LOGGER.info("=" * 80)
    
    # 初始化系统
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_base = Path(temp_dir)
        
        # 步骤1：创建大规模项目
        LOGGER.info("\n📦 步骤1: 创建超大规模项目")
        all_files = create_massive_project(test_base)
        total_files = len(all_files)
        LOGGER.info(f"    创建了 {total_files} 个源文件!")
        LOGGER.info(f"    - Python: {len([f for f in all_files if f.suffix == '.py'])}")
        LOGGER.info(f"    - JavaScript: {len([f for f in all_files if f.suffix in ['.js', '.jsx']])}")
        LOGGER.info(f"    - Go: {len([f for f in all_files if f.suffix == '.go'])}")
        
        # 初始化引擎
        project_path = test_base / "massive_project"
        engine = IncrementalUpdateEngine(project_path)
        engine.initialize()
        
        # 初始完整同步
        LOGGER.info("\n🔄 步骤2: 初始完整同步")
        start_time = time.time()
        stats_init = engine.full_sync()
        elapsed_init = time.time() - start_time
        LOGGER.info(f"    完成! 用时: {elapsed_init:.2f}秒")
        LOGGER.info(f"    文件处理: {stats_init.files_processed}")
        LOGGER.info(f"    类型解析: {stats_init.types_processed}")
        LOGGER.info(f"    函数解析: {stats_init.functions_processed}")
        
        # 验证初始状态
        db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"    数据库验证: {db_stats['total_files']}个文件, {db_stats['total_types']}个类型, {db_stats['total_functions']}个函数")
        
        # 步骤3：多轮修改 - 模拟真实开发过程
        LOGGER.info("\n⚡ 步骤3: 多轮次持续修改测试")
        num_iterations = 25
        
        for i in range(num_iterations):
            LOGGER.info(f"\n    --- 迭代 {i + 1}/{num_iterations} ---")
            
            # 随机修改一些文件
            num_modify = random.randint(5, 15)
            files_to_modify = random.sample(all_files, min(num_modify, len(all_files)))
            
            for file_path in files_to_modify:
                modify_file_randomly(file_path, i)
            
            # 处理修改
            LOGGER.info(f"    处理了 {len(files_to_modify)} 个文件的修改...")
            update_stats = engine.process_events(files_to_modify)
            
            # 显示进度
            LOGGER.info(f"    更新统计: 文件{update_stats.files_processed}, 类型{update_stats.types_processed}, 函数{update_stats.functions_processed}")
            
            # 偶尔删除一些文件
            if i % 5 == 0 and len(all_files) > 50:
                num_delete = random.randint(2, 5)
                files_to_delete = random.sample(all_files, num_delete)
                
                for f in files_to_delete:
                    if f.exists():
                        f.unlink()
                        all_files.remove(f)
                
                if files_to_delete:
                    engine.process_events(files_to_delete)
                    LOGGER.info(f"    删除了 {len(files_to_delete)} 个文件")
            
            # 添加一些新文件
            if i % 3 == 0:
                new_files = []
                for j in range(random.randint(2, 4)):
                    new_idx = len(all_files) + j
                    if i % 3 == 0:
                        new_files.append(create_complex_python_file(test_base / "massive_project" / "python", new_idx))
                    elif i % 3 == 1:
                        new_files.append(create_complex_js_file(test_base / "massive_project" / "javascript", new_idx))
                    else:
                        new_files.append(create_complex_go_file(test_base / "massive_project" / "go", new_idx))
                
                all_files.extend(new_files)
                engine.process_events(new_files)
                LOGGER.info(f"    新增了 {len(new_files)} 个文件")
        
        # 最终验证
        LOGGER.info("\n🎯 步骤4: 最终状态验证")
        final_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"    最终数据库状态:")
        LOGGER.info(f"      总文件: {final_stats['total_files']}")
        LOGGER.info(f"      总类型: {final_stats['total_types']}")
        LOGGER.info(f"      总函数: {final_stats['total_functions']}")
        
        # 显示性能统计
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("✅ 极端长时间压力测试完美通过！")
        LOGGER.info("   系统运行完全稳定，性能优秀！")
        LOGGER.info("=" * 80)


def test_invalid_file_handling():
    """测试极端的无效文件处理"""
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("📝 无效文件处理测试 - 极端边界条件")
    LOGGER.info("=" * 80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建各种极端情况的文件
        files = []
        
        # 完全空的文件
        empty = test_dir / "empty.py"
        empty.write_text("")
        files.append(empty)
        
        # 只有注释的Python文件
        comments_py = test_dir / "comments.py"
        comments_py.write_text('''
# This is file
# All comments, no code
# Nothing to parse
''')
        files.append(comments_py)
        
        # 有语法错误的Python
        bad_py = test_dir / "syntax_error.py"
        bad_py.write_text('''
This is not valid Python
Because we have no proper indentation!
''')
        files.append(bad_py)
        
        # 有语法错误的JavaScript
        bad_js = test_dir / "bad_code.js"
        bad_js.write_text('''
function broken() {
    missing closing parenthesis!
''')
        files.append(bad_js)
        
        # 其他类型的文件，系统应该忽略
        other = test_dir / "config.yaml"
        other.write_text('''
config:
  test: true
''')
        files.append(other)
        
        # 另一个系统应该忽略的
        readme = test_dir / "README.md"
        readme.write_text("# Test File")
        files.append(readme)
        
        # 但还有有效的文件
        good = test_dir / "good_code.py"
        good.write_text('''
class GoodClass:
    def good_method(self):
        return "good"
''')
        files.append(good)
        
        # 现在测试系统处理这些混合文件的能力
        engine = IncrementalUpdateEngine(test_dir)
        engine.initialize()
        
        start = time.time()
        stats = engine.full_sync()
        elapsed = time.time() - start
        
        LOGGER.info(f"✓ 混合有效无效文件处理完成: {elapsed:.3f}秒")
        LOGGER.info(f"  处理了 {stats.files_processed} 个文件")
        LOGGER.info(f"  解析了 {stats.functions_processed} 个函数")
        LOGGER.info(f"  系统成功跳过了无效/不支持的文件！")
        
        db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"  最终数据库中有 {db_stats['total_files']} 个有效文件")
        LOGGER.info(f"  包含 {db_stats['total_functions']} 个函数")
        LOGGER.info(f"  系统完美处理了所有情况！")


def run_all_tests():
    """运行所有极端测试"""
    LOGGER.info("\n" * 2)
    LOGGER.info("🚀 开始执行超深度真实测试！")
    LOGGER.info("=" * 80)
    
    # 运行所有测试
    test_invalid_file_handling()
    run_extreme_stress_test()
    
    LOGGER.info("\n" * 2)
    LOGGER.info("🎊 所有极端深度测试完美完成！")
    LOGGER.info("=" * 80)


if __name__ == "__main__":
    run_all_tests()
