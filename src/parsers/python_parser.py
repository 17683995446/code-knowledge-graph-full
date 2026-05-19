"""
Python Parser Module
Using tree-sitter-python for accurate Python code parsing
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from .universal_parser import UniversalParser, ParseResult, ParserRegistry
from ..core.configuration import LOGGER

try:
    from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class PythonParser(UniversalParser):
    """
    Python parser supporting .py files
    Uses tree-sitter when available, falls back to regex-based parsing
    """
    
    LANGUAGE_NAME = "python"
    FILE_EXTENSIONS = ('.py', '.pyw')
    
    def __init__(self):
        self._tree_sitter_parser = None
        self._function_pattern = re.compile(
            r'^(?:async\s+)?def\s+(\w+)\s*\([^)]*\)',
            re.MULTILINE
        )
        self._class_pattern = re.compile(
            r'^class\s+(\w+)(?:\s*\([^)]*\))?\s*:',
            re.MULTILINE
        )
        self._import_pattern = re.compile(
            r'^(?:from\s+([\w.]+)\s+)?import\s+(.+)',
            re.MULTILINE
        )
        self._call_pattern = re.compile(
            r'(\b\w+)\s*\('
        )
        
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter()
    
    def _init_tree_sitter(self) -> None:
        """Initialize tree-sitter parser if available"""
        try:
            self._tree_sitter_parser = get_parser('python')
            LOGGER.info("Python parser initialized with tree-sitter")
        except Exception as e:
            LOGGER.warning(f"Tree-sitter not available for Python: {e}")
            self._tree_sitter_parser = None
    
    def parse(self, file_path: Path) -> ParseResult:
        """Parse Python file"""
        LOGGER.debug(f"Parsing Python file: {file_path}")
        
        result = ParseResult(
            file_path=str(file_path),
            language=self.LANGUAGE_NAME,
            file_hash=self.compute_file_hash(file_path),
            modified_time=self.get_modified_time(file_path)
        )
        
        try:
            content = self.read_file_content(file_path)
            lines = content.split('\n')
            
            if self._tree_sitter_parser:
                self._parse_with_tree_sitter(result, content, lines)
            else:
                self._parse_with_regex(result, content, lines)
            
        except Exception as e:
            LOGGER.error(f"Error parsing {file_path}: {e}")
            result.errors.append(str(e))
        
        return result
    
    def get_language(self) -> str:
        """Get language name"""
        return self.LANGUAGE_NAME
    
    def _parse_with_tree_sitter(
        self,
        result: ParseResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Parse using tree-sitter for accurate results"""
        try:
            tree = self._tree_sitter_parser.parse(bytes(content, 'utf8'))
            
            self._extract_tree_sitter_nodes(tree.root_node, result, content, lines)
            self._resolve_function_calls(result, content)
            
        except Exception as e:
            LOGGER.warning(f"Tree-sitter parsing failed, falling back to regex: {e}")
            self._parse_with_regex(result, content, lines)
    
    def _extract_tree_sitter_nodes(
        self,
        node,
        result: ParseResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Recursively extract nodes from tree-sitter parse tree"""
        node_type = node.type
        start_point = node.start_point[0] + 1
        end_point = node.end_point[0] + 1
        
        if node_type == 'class_definition':
            name_node = None
            base_nodes = []
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                elif child.type == 'argument_list':
                    for arg_child in child.children:
                        if arg_child.type == 'identifier':
                            base_nodes.append(arg_child.text.decode('utf8'))
            
            if name_node:
                type_info = {
                    'name': name_node.text.decode('utf8'),
                    'kind': 'class',
                    'start_line': start_point,
                    'end_line': end_point,
                    'flags': 0,
                    'base_classes': base_nodes,
                    'docstring': self._extract_docstring_from_range(lines, start_point)
                }
                result.types.append(type_info)
        
        elif node_type == 'function_definition':
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if name_node:
                func_info = {
                    'name': name_node.text.decode('utf8'),
                    'start_line': start_point,
                    'end_line': end_point,
                    'signature': self._extract_signature(lines, start_point),
                    'type_id': None,
                    'docstring': self._extract_docstring_from_range(lines, start_point),
                    'calls': []
                }
                result.functions.append(func_info)
        
        for child in node.children:
            self._extract_tree_sitter_nodes(child, result, content, lines)
    
    def _parse_with_regex(
        self,
        result: ParseResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Regex-based parsing for Python using indentation"""
        current_class = None
        class_indent = 0
        file_indent = 0
        
        entities = []
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            indent = len(line) - len(stripped)
            current_line_num = i + 1
            
            class_match = self._class_pattern.match(stripped)
            if class_match and indent == file_indent:
                class_name = class_match.group(1)
                current_class = class_name
                class_indent = indent
                
                result.types.append({
                    'name': class_name,
                    'kind': 'class',
                    'start_line': current_line_num,
                    'end_line': current_line_num,
                    'flags': 0,
                    'base_classes': []
                })
                continue
            
            if current_class is not None and indent <= class_indent:
                current_class = None
            
            func_match = self._function_pattern.match(stripped)
            if func_match:
                func_name = func_match.group(1)
                func_indent = indent
                func_start = current_line_num
                
                func_end = self._find_function_end(lines, i + 1, func_indent)
                
                type_id = current_class if current_class and func_indent > class_indent else None
                
                func_info = {
                    'name': func_name,
                    'start_line': func_start,
                    'end_line': func_end,
                    'signature': self._extract_signature(lines, func_start),
                    'type_id': type_id,
                    'calls': []
                }
                result.functions.append(func_info)
                continue
            
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_match = self._import_pattern.match(stripped)
                if import_match:
                    module_from = import_match.group(1)
                    imports = import_match.group(2)
                    
                    imported_names = []
                    for imp in imports.split(','):
                        imp = imp.strip()
                        if imp and imp != '*':
                            if ' as ' in imp:
                                imp = imp.split(' as ')[0].strip()
                            imported_names.append(imp)
                    
                    result.imports.append({
                        'module_path': module_from or '',
                        'imported_names': imported_names,
                        'is_wildcard': '*' in imports
                    })
        
        self._resolve_function_calls(result, content)
    
    def _find_function_end(self, lines: List[str], start_line: int, func_indent: int) -> int:
        """Find the end line of a function using indentation"""
        for i in range(start_line, len(lines)):
            line = lines[i]
            stripped = line.lstrip()
            
            if not stripped or stripped.startswith('#'):
                continue
            
            indent = len(line) - len(stripped)
            
            if indent <= func_indent:
                return i
            
            return i + 1
        
        return len(lines)
    
    def _resolve_function_calls(
        self,
        result: ParseResult,
        content: str
    ) -> None:
        """Resolve function calls within functions"""
        known_functions = {f['name'] for f in result.functions}
        
        class_methods: Dict[str, str] = {}
        for func in result.functions:
            if func.get('type_id'):
                class_methods[func['name']] = func['type_id']
        
        lines = content.split('\n')
        
        for func in result.functions:
            func_start = func['start_line'] - 1
            func_end = min(func['end_line'], len(lines))
            
            if func_end <= func_start:
                func_end = func_start + 1
            
            func_lines = lines[func_start:func_end]
            func_content = '\n'.join(func_lines)
            
            calls = []
            for match in self._call_pattern.finditer(func_content):
                called_name = match.group(1)
                
                if called_name not in known_functions:
                    continue
                if called_name == func['name']:
                    continue
                
                if func['type_id'] and class_methods.get(called_name) == func['type_id']:
                    calls.append(called_name)
                elif not func['type_id']:
                    calls.append(called_name)
            
            func['calls'] = list(set(calls))
    
    def _extract_docstring_from_range(
        self,
        lines: List[str],
        start_line: int
    ) -> Optional[str]:
        """Extract docstring from function/class definition"""
        if start_line < 2:
            return None
        
        prev_lines = lines[max(0, start_line-3):start_line-1]
        
        for line in prev_lines:
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                return stripped.strip('"\'').strip()
        
        return None
    
    def _extract_signature(self, lines: List[str], start_line: int) -> str:
        """Extract function signature"""
        if start_line > len(lines):
            return ""
        
        signature_parts = []
        for i in range(start_line - 1, min(start_line + 2, len(lines))):
            signature_parts.append(lines[i].strip())
            if ':' in lines[i] and not lines[i].strip().endswith(':'):
                break
        
        return ' '.join(signature_parts).rstrip(':').strip() + ':'


def register_python_parser() -> PythonParser:
    """Register Python parser with the global registry"""
    parser = PythonParser()
    ParserRegistry.register(parser)
    return parser
