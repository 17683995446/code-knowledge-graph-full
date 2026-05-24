#!/usr/bin/env python3
"""测试JSX文件解析"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.parsers import initialize_all_parsers, get_parser_for_file


def test_jsx_parsing():
    """测试JSX文件解析"""
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        jsx_file = temp_path / "test.jsx"
        jsx_file.write_text("""
import React from 'react';

class TestComponent {
    render() {
        return <div>Test</div>;
    }
}

export function helperFunction(x, y) {
    return x + y;
}
""")
        
        print(f"测试文件: {jsx_file}")
        print(f"文件后缀: {jsx_file.suffix}")
        
        parser = get_parser_for_file(jsx_file)
        print(f"解析器: {parser}")
        print(f"解析器语言: {parser.LANGUAGE_NAME if parser else 'None'}")
        print(f"解析器扩展名: {parser.FILE_EXTENSIONS if parser else 'None'}")
        
        if parser:
            result = parser.parse(jsx_file)
            print(f"\n解析结果:")
            print(f"  语言: {result.language}")
            print(f"  类型: {len(result.types)}")
            for t in result.types:
                print(f"    - {t}")
            print(f"  函数: {len(result.functions)}")
            for f in result.functions:
                print(f"    - {f}")
            print(f"  错误: {result.errors}")


if __name__ == "__main__":
    test_jsx_parsing()
