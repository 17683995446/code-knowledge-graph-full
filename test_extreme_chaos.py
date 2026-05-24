#!/usr/bin/env python3
"""
Extreme Chaos Test - Multi-Dimension Real-World Scenario
Slow but thorough testing following slow-and-steady principle
"""

import sys
import time
import tempfile
import random
import os
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def create_chaos_project(base_dir: Path) -> List[Path]:
    """Create an extreme chaotic test project following real-world scenario"""
    project_root = base_dir / "extreme-chaos-project"
    project_root.mkdir(exist_ok=True)
    
    all_files: List[Path] = []
    
    # 1. Create deeply nested directory structure (extreme nesting)
    LOGGER.info("Creating deeply nested directories...")
    nested_dir = project_root
    for i in range(15):
        nested_dir = nested_dir / f"level_{i}"
        nested_dir.mkdir(exist_ok=True)
        
        # Create files at every nested level
        for lang, ext in [("py", "py"), ("js", "jsx"), ("go", "go")]:
            f = nested_dir / f"nested_{lang}.{ext}"
            f.write_text(create_random_content(lang, i))
            all_files.append(f)
    
    # 2. Create mixed directory with all languages combined
    LOGGER.info("Creating mixed language directory...")
    mixed_dir = project_root / "mixed_languages"
    mixed_dir.mkdir(exist_ok=True)
    
    for i in range(30):
        lang = random.choice(["py", "js", "jsx", "go"])
        ext_map = {"py": "py", "js": "js", "jsx": "jsx", "go": "go"}
        f = mixed_dir / f"mixed_file_{i:03d}.{ext_map[lang]}"
        f.write_text(create_random_content(lang, i))
        all_files.append(f)
    
    # 3. Create invalid and corrupted files (for error handling testing)
    LOGGER.info("Creating invalid/corrupted test files...")
    invalid_dir = project_root / "invalid_and_corrupted"
    invalid_dir.mkdir(exist_ok=True)
    
    # Empty files
    for i in range(5):
        f = invalid_dir / f"empty_{i}.py"
        f.write_text("")
        all_files.append(f)
    
    # Only comments
    for i in range(5):
        f = invalid_dir / f"comments_only_{i}.js"
        f.write_text("""
// This file has nothing but comments
/* Multi-line comment
   Still nothing! */
""")
        all_files.append(f)
    
    # Corrupted Python (syntax errors)
    f = invalid_dir / "corrupted_python.py"
    f.write_text("""
def broken_function(
    this is bad syntax
    return nothing
""")
    all_files.append(f)
    
    # Corrupted JS
    f = invalid_dir / "corrupted_js.jsx"
    f.write_text("""
function brokenComponent() {
    <div>Broken
    return <div />
}
""")
    all_files.append(f)
    
    # Corrupted Go
    f = invalid_dir / "corrupted_go.go"
    f.write_text("""
package main

func broken() {
    broken = true
    return nil
}
""")
    all_files.append(f)
    
    # 4. Special characters in filenames
    LOGGER.info("Creating files with special characters...")
    special_dir = project_root / "special_chars"
    special_dir.mkdir(exist_ok=True)
    
    for i in range(10):
        # Special characters in filenames
        filename = f"!@#$%^&*()_file_{i}@.py"
        f = special_dir / filename
        f.write_text(f"""
def func_{i}(x):
    return x + {i}
""")
        all_files.append(f)
    
    # 5. Large, complex files with multiple entities
    LOGGER.info("Creating large complex files...")
    large_dir = project_root / "large_complex"
    large_dir.mkdir(exist_ok=True)
    
    # Super complex Python file
    f = large_dir / "super_complex.py"
    f.write_text(create_complex_python_file())
    all_files.append(f)
    
    # Super complex JS file
    f = large_dir / "super_complex.jsx"
    f.write_text(create_complex_js_file())
    all_files.append(f)
    
    # Super complex Go file
    f = large_dir / "super_complex.go"
    f.write_text(create_complex_go_file())
    all_files.append(f)
    
    # 6. Realistic project structure
    LOGGER.info("Creating realistic project structure...")
    realistic_dir = project_root / "realistic_project"
    realistic_dir.mkdir(exist_ok=True)
    
    (realistic_dir / "src").mkdir(exist_ok=True)
    (realistic_dir / "src" / "models").mkdir(exist_ok=True)
    (realistic_dir / "src" / "services").mkdir(exist_ok=True)
    (realistic_dir / "src" / "controllers").mkdir(exist_ok=True)
    (realistic_dir / "tests").mkdir(exist_ok=True)
    (realistic_dir / "docs").mkdir(exist_ok=True)
    
    for i in range(10):
        f = realistic_dir / "src" / "models" / f"model_{i}.py"
        f.write_text(f"""
class Model{i}:
    def __init__(self, data):
        self.data = data
    
    def validate(self):
        return len(self.data) > 0
    
    def save(self):
        pass
""")
        all_files.append(f)
        
        f = realistic_dir / "src" / "services" / f"service_{i}.py"
        f.write_text(f"""
from .models import Model{i}

class Service{i}:
    def __init__(self):
        self.things = []
    
    def do_stuff(self):
        m = Model{i}(data={{}})
        return m
""")
        all_files.append(f)
    
    return all_files


def create_random_content(lang: str, seed: int) -> str:
    """Create random content based on language"""
    random.seed(seed)
    
    if lang == "py":
        return f"""
class RandomClass{seed}:
    def method1(self):
        return {seed}
    
    def method2(self, x):
        return x + {seed}

def random_func{seed}(x):
    return x * {seed}
"""
    elif lang in ["js", "jsx"]:
        return f"""
export class RandomClass{seed} {{
    method1() {{
        return {seed};
    }}
    
    method2(x) {{
        return x + {seed};
    }}
}}

export function randomFunc{seed}(x) {{
    return x * {seed};
}}
"""
    elif lang == "go":
        return f"""
package main

type RandomStruct{seed} struct {{
    Value int
}}

func (r *RandomStruct{seed}) Method1() int {{
    return {seed};
}}

func RandomFunc{seed}(x int) int {{
    return x * {seed};
}}
"""
    else:
        return ""


def create_complex_python_file() -> str:
    """Create a very complex Python file"""
    return """
class BaseClass:
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def process(self, data):
        return data


class SubClass1(BaseClass):
    def __init__(self, name, config):
        super().__init__(name)
        self.config = config
    
    def process(self, data):
        result = super().process(data)
        return {k: v for k, v in result.items()}
    
    def validate(self, value):
        return value is not None


class SubClass2(BaseClass):
    def __init__(self, name, extra):
        super().__init__(name)
        self.extra = extra
    
    def do_something(self):
        return self.extra * 2


class SubSubClass(SubClass1):
    def __init__(self, name, config, mode):
        super().__init__(name, config)
        self.mode = mode
    
    def advanced_process(self, data):
        return self.process(data) * self.mode


def utility_function1(x, y):
    return x + y


def utility_function2(a, b, c):
    return (a + b) * c


def helper_function(data):
    return utility_function1(data['x'], data['y'])


def main():
    obj1 = SubClass1("test1", {'a': 1})
    obj2 = SubSubClass("test2", {'b': 2}, 3)
    
    result1 = obj1.process({'key': 'value'})
    result2 = obj2.advanced_process({'x': 10, 'y': 20})
    
    return {
        'result1': result1,
        'result2': result2
    }


if __name__ == "__main__":
    print(main())
"""


def create_complex_js_file() -> str:
    """Create a very complex JavaScript file"""
    return """
export class BaseComponent {
    constructor(name) {
        this.name = name;
    }
    
    getName() {
        return this.name;
    }
    
    render() {
        return <div>{this.name}</div>;
    }
}


export class SubComponent1 extends BaseComponent {
    constructor(name, config) {
        super(name);
        this.config = config;
    }
    
    render() {
        return (
            <div className="component">
                <h2>{this.name}</h2>
                <span>Config: {JSON.stringify(this.config)}</span>
            </div>
        );
    }
}


export class SubComponent2 extends BaseComponent {
    constructor(name, extra) {
        super(name);
        this.extra = extra;
    }
    
    doSomething() {
        return this.extra * 2;
    }
}


export function utilityFunction1(x, y) {
    return x + y;
}


export function utilityFunction2(a, b, c) {
    return (a + b) * c;
}


export function helperFunction(data) {
    return utilityFunction1(data.x, data.y);
}


export function main() {
    const obj1 = new SubComponent1("test1", {a: 1});
    const obj2 = new SubComponent2("test2", 3);
    
    const result1 = helperFunction({x: 10, y: 20});
    const result2 = obj2.doSomething();
    
    return {result1, result2};
}
"""


def create_complex_go_file() -> str:
    """Create a very complex Go file"""
    return """
package main

import "fmt"

type BaseInterface interface {
    GetName() string
    Process(data map[string]interface{}) map[string]interface{}
}


type BaseStruct struct {
    Name string
}


func (b *BaseStruct) GetName() string {
    return b.Name
}


func (b *BaseStruct) Process(data map[string]interface{}) map[string]interface{} {
    return data
}


type SubStruct1 struct {
    BaseStruct
    Config map[string]interface{}
}


func (s *SubStruct1) Process(data map[string]interface{}) map[string]interface{} {
    result := s.BaseStruct.Process(data)
    processed := make(map[string]interface{})
    for k, v := range result {
        processed[k] = v
    }
    return processed
}


func (s *SubStruct1) Validate(value interface{}) bool {
    return value != nil
}


type SubStruct2 struct {
    BaseStruct
    Extra int
}


func (s *SubStruct2) DoSomething() int {
    return s.Extra * 2
}


func UtilityFunction1(x, y int) int {
    return x + y
}


func UtilityFunction2(a, b, c int) int {
    return (a + b) * c
}


func HelperFunction(data map[string]int) int {
    return UtilityFunction1(data["x"], data["y"])
}


func main() {
    obj1 := &SubStruct1{
        BaseStruct: BaseStruct{Name: "test1"},
        Config: map[string]interface{}{"a": 1},
    }
    
    obj2 := &SubStruct2{
        BaseStruct: BaseStruct{Name: "test2"},
        Extra: 3,
    }
    
    data := map[string]int{"x": 10, "y": 20}
    
    result1 := HelperFunction(data)
    result2 := obj2.DoSomething()
    
    fmt.Printf("Result1: %v\\n", result1)
    fmt.Printf("Result2: %v\\n", result2)
}
"""


def run_extreme_chaos_test():
    """Run the extreme chaos test - slow but thorough"""
    LOGGER.info("=" * 80)
    LOGGER.info("Extreme Chaos Test - Slow and Steady")
    LOGGER.info("=" * 80)
    
    # Initialize parsers
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the chaos project
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Step 1: Creating chaos project")
        all_files = create_chaos_project(Path(temp_dir))
        
        project_root = Path(temp_dir) / "extreme-chaos-project"
        LOGGER.info(f"Created {len(all_files)} files in chaotic structure")
        
        # Initialize engine
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Step 2: Initializing engine")
        engine = IncrementalUpdateEngine(project_root)
        engine.initialize()
        
        # First sync
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Step 3: Performing initial full sync")
        start = time.time()
        stats = engine.full_sync()
        elapsed = time.time() - start
        
        LOGGER.info(f"Initial sync complete in {elapsed:.3f}s")
        LOGGER.info(f"  Files: {stats.files_processed}")
        LOGGER.info(f"  Types: {stats.types_processed}")
        LOGGER.info(f"  Functions: {stats.functions_processed}")
        LOGGER.info(f"  Calls: {stats.calls_resolved}")
        
        # Validate database state
        db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info("\nDatabase stats:")
        LOGGER.info(f"  Files: {db_stats['total_files']}")
        LOGGER.info(f"  Types: {db_stats['total_types']}")
        LOGGER.info(f"  Functions: {db_stats['total_functions']}")
        
        # Verify cache consistency
        LOGGER.info("\nCache validation:")
        LOGGER.info(f"  File cache: {len(engine._file_id_cache)}")
        LOGGER.info(f"  Type cache: {len(engine._type_cache)}")
        LOGGER.info(f"  Func cache: {len(engine._function_cache)}")
        
        # Step 4: Slow modifications - one by one for better debugging
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Step 4: Slow file modifications (one at a time)")
        
        num_modify = min(20, len(all_files))
        for i in range(num_modify):
            # Pick and modify a file
            file_to_modify = random.choice(all_files)
            
            if file_to_modify.exists():
                LOGGER.info(f"\nModifying {i+1}/{num_modify}: {file_to_modify.name}")
                
                content = file_to_modify.read_text()
                added_content = f"""

# Added in chaos test round {i}
def chaos_function_{i}(x):
    return x + {i}
"""
                if file_to_modify.suffix == ".py":
                    new_content = content + added_content
                else:
                    new_content = content + f"""

// Added in chaos test round {i}
function chaosFunction{i}(x) {{
    return x + {i};
}}
"""
                
                file_to_modify.write_text(new_content)
                
                # Process the change
                update_stats = engine.process_events([file_to_modify])
                
                # Log the results
                LOGGER.info(f"  Processed: F={update_stats.files_processed} T={update_stats.types_processed} Fn={update_stats.functions_processed}")
                
                # Verify state after each change
                current_db = DATABASE_CONNECTION.get_database_stats()
                cache_ok = (
                    len(engine._file_id_cache) == current_db['total_files'] and
                    len(engine._type_cache) == current_db['total_types'] and
                    len(engine._function_cache) == current_db['total_functions']
                )
                LOGGER.info(f"  Cache OK: {cache_ok}")
        
        # Step 5: Random deletions
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Step 5: Random file deletions")
        
        num_delete = min(10, len(all_files))
        for i in range(num_delete):
            file_to_delete = random.choice(all_files)
            if file_to_delete.exists() and file_to_delete.is_file():
                LOGGER.info(f"\nDeleting {i+1}/{num_delete}: {file_to_delete.name}")
                
                file_to_delete.unlink()
                
                if file_to_delete in all_files:
                    all_files.remove(file_to_delete)
                
                # Process the deletion
                engine.process_events([file_to_delete])
                
                # Verify
                current_db = DATABASE_CONNECTION.get_database_stats()
                LOGGER.info(f"  DB now: F={current_db['total_files']} T={current_db['total_types']} Fn={current_db['total_functions']}")
        
        # Final verification
        LOGGER.info("\n" + "=" * 80)
        LOGGER.info("Final Verification")
        
        final_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"Final database:")
        LOGGER.info(f"  Files: {final_stats['total_files']}")
        LOGGER.info(f"  Types: {final_stats['total_types']}")
        LOGGER.info(f"  Functions: {final_stats['total_functions']}")
        
        final_cache_ok = (
            len(engine._file_id_cache) == final_stats['total_files'] and
            len(engine._type_cache) == final_stats['total_types'] and
            len(engine._function_cache) == final_stats['total_functions']
        )
        
        LOGGER.info(f"\n" + "=" * 80)
        if final_cache_ok:
            LOGGER.info("✅ SUCCESS: Cache perfectly consistent with database!")
        else:
            LOGGER.error("❌ PROBLEM: Cache inconsistency detected!")
        LOGGER.info("=" * 80)
        
        return final_cache_ok


if __name__ == "__main__":
    try:
        result = run_extreme_chaos_test()
        if result:
            LOGGER.info("\n🎉 Extreme Chaos Test PASSED!")
        else:
            LOGGER.info("\n❌ Extreme Chaos Test FAILED - Issues Found")
    except Exception as e:
        LOGGER.error(f"\n❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
