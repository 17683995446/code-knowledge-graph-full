"""
Unit Tests for Parser Module
"""

import unittest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsers.universal_parser import (
    UniversalParser, ParseResult, ParserRegistry,
    detect_language
)
from src.parsers.python_parser import PythonParser
from src.parsers.go_parser import GoParser
from src.parsers.javascript_parser import JavaScriptParser


class TestPythonParser(unittest.TestCase):
    """Test cases for PythonParser"""
    
    def setUp(self):
        self.parser = PythonParser()
        self.temp_files = []
    
    def tearDown(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_file(self, content, suffix='.py'):
        """Create a temporary file with content"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, content.encode())
        os.close(fd)
        self.temp_files.append(path)
        return Path(path)
    
    def test_parse_simple_class(self):
        """Test parsing a simple class"""
        content = '''
class MyClass:
    """A simple class"""
    def __init__(self):
        pass
    
    def method(self):
        pass
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertEqual(result.language, 'python')
        self.assertEqual(len(result.types), 1)
        self.assertEqual(result.types[0]['name'], 'MyClass')
        self.assertEqual(result.types[0]['kind'], 'class')
    
    def test_parse_simple_function(self):
        """Test parsing a simple function"""
        content = '''
def hello_world():
    """Print hello"""
    print("Hello, World!")

def add(a, b):
    return a + b
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertEqual(len(result.functions), 2)
        func_names = [f['name'] for f in result.functions]
        self.assertIn('hello_world', func_names)
        self.assertIn('add', func_names)
    
    def test_parse_imports(self):
        """Test parsing imports"""
        content = '''
import os
import sys
from pathlib import Path
from collections import defaultdict, OrderedDict
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertGreaterEqual(len(result.imports), 4)
    
    def test_parse_empty_file(self):
        """Test parsing empty file"""
        file_path = self.create_temp_file('')
        result = self.parser.parse(file_path)
        
        self.assertEqual(result.language, 'python')
        self.assertEqual(len(result.types), 0)
        self.assertEqual(len(result.functions), 0)


class TestGoParser(unittest.TestCase):
    """Test cases for GoParser"""
    
    def setUp(self):
        self.parser = GoParser()
        self.temp_files = []
    
    def tearDown(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_file(self, content, suffix='.go'):
        """Create a temporary file with content"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, content.encode())
        os.close(fd)
        self.temp_files.append(path)
        return Path(path)
    
    def test_parse_struct(self):
        """Test parsing a struct"""
        content = '''
package main

type User struct {
    Name string
    Age  int
}
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertEqual(result.language, 'go')
        self.assertEqual(len(result.types), 1)
        self.assertEqual(result.types[0]['name'], 'User')
        self.assertEqual(result.types[0]['kind'], 'struct')
    
    def test_parse_interface(self):
        """Test parsing an interface"""
        content = '''
package main

type Reader interface {
    Read(p []byte) (n int, err error)
}
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertEqual(result.language, 'go')
        self.assertEqual(len(result.types), 1)
        self.assertEqual(result.types[0]['name'], 'Reader')
        self.assertEqual(result.types[0]['kind'], 'interface')
    
    def test_parse_function(self):
        """Test parsing a function"""
        content = '''
package main

func main() {
    println("Hello")
}

func add(a, b int) int {
    return a + b
}
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertGreaterEqual(len(result.functions), 2)
        func_names = [f['name'] for f in result.functions]
        self.assertIn('main', func_names)
        self.assertIn('add', func_names)


class TestJavaScriptParser(unittest.TestCase):
    """Test cases for JavaScriptParser"""
    
    def setUp(self):
        self.parser = JavaScriptParser()
        self.temp_files = []
    
    def tearDown(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_file(self, content, suffix='.js'):
        """Create a temporary file with content"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, content.encode())
        os.close(fd)
        self.temp_files.append(path)
        return Path(path)
    
    def test_parse_class(self):
        """Test parsing a JavaScript class"""
        content = '''
class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        console.log(this.name + ' makes a noise.');
    }
}
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        self.assertEqual(result.language, 'javascript')
        self.assertEqual(len(result.types), 1)
        self.assertEqual(result.types[0]['name'], 'Animal')
    
    def test_parse_function(self):
        """Test parsing JavaScript function"""
        content = '''
function greet(name) {
    return "Hello, " + name;
}

const arrow = (x) => x * 2;
'''
        file_path = self.create_temp_file(content)
        result = self.parser.parse(file_path)
        
        func_names = [f['name'] for f in result.functions]
        self.assertIn('greet', func_names)


class TestParserRegistry(unittest.TestCase):
    """Test cases for ParserRegistry"""
    
    @classmethod
    def setUpClass(cls):
        from src.parsers import initialize_all_parsers
        initialize_all_parsers()
    
    def test_detect_language(self):
        """Test language detection from extension"""
        self.assertEqual(detect_language(Path('test.py')), 'python')
        self.assertEqual(detect_language(Path('test.go')), 'go')
        self.assertEqual(detect_language(Path('test.js')), 'javascript')
        detected_ts = detect_language(Path('test.ts'))
        self.assertIn(detected_ts, ['typescript', 'arkts'])
        detected_ets = detect_language(Path('test.ets'))
        self.assertEqual(detected_ets, 'arkts')
    
    def test_parser_registration(self):
        """Test parser registration"""
        parsers = ParserRegistry.get_all_parsers()
        self.assertIn('python', parsers)
        self.assertIn('go', parsers)
        self.assertIn('javascript', parsers)
        self.assertIn('arkts', parsers)


class TestParseResult(unittest.TestCase):
    """Test cases for ParseResult"""
    
    def test_is_valid_with_content(self):
        """Test is_valid returns True with content"""
        result = ParseResult(
            file_path='/test.py',
            language='python',
            file_hash=b'test',
            modified_time=1234567890,
            functions=[{'name': 'test'}]
        )
        self.assertTrue(result.is_valid())
    
    def test_is_valid_without_content(self):
        """Test is_valid returns False without content"""
        result = ParseResult(
            file_path='/test.py',
            language='python',
            file_hash=b'test',
            modified_time=1234567890
        )
        self.assertFalse(result.is_valid())


if __name__ == '__main__':
    unittest.main()
