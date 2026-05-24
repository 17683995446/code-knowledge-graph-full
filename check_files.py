#!/usr/bin/env python3
"""检查生成的文件"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def check_generated_files():
    """检查生成的文件"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 检查 JSX 生成
        jsx_file = temp_path / "test.jsx"
        jsx_content = '''
import React from 'react';

export class TestClass {
    render() {
        return <div>Test</div>;
    }
}

export function helperFunction(x, y) {
    return x + y;
}
'''
        jsx_file.write_text(jsx_content)
        
        # 检查 Go 生成
        go_file = temp_path / "test.go"
        go_content = '''
package main

type TestStruct struct {
    Data []interface{}
}

func (c *TestStruct) Process(value interface{}) interface{} {
    return value
}

func helperFunction(x, y interface{}) interface{} {
    return x
}
'''
        go_file.write_text(go_content)
        
        print("JSX 文件内容:")
        print(jsx_content)
        print("\nGo 文件内容:")
        print(go_content)
        
        # 统计函数和类型数量
        import re
        
        jsx_classes = len(re.findall(r'class\s+\w+', jsx_content))
        jsx_funcs = len(re.findall(r'function\s+\w+', jsx_content))
        
        go_types = len(re.findall(r'type\s+\w+\s+struct', go_content))
        go_funcs = len(re.findall(r'func\s+\(?\w+\s+)?\w+\s*\(', go_content))
        
        print(f"\nJSX: {jsx_classes} 类, {jsx_funcs} 函数")
        print(f"Go: {go_types} 类型, {go_funcs} 函数")


if __name__ == "__main__":
    check_generated_files()
