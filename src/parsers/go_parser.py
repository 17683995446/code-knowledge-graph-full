"""
Go Parser Module
Using tree-sitter-go for accurate Go code parsing
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from .universal_parser import UniversalParser, ParseResult, ParserRegistry
from ..core.configuration import LOGGER

try:
    from tree_sitter_languages import get_parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False


class GoParser(UniversalParser):
    """
    Go parser supporting .go files
    Uses tree-sitter when available
    """
    
    LANGUAGE_NAME = "go"
    FILE_EXTENSIONS = ('.go',)
    
    def __init__(self):
        self._tree_sitter_parser = None
        self._function_pattern = re.compile(
            r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\([^)]*\)'
        )
        self._method_pattern = re.compile(
            r'func\s+\([^)]+\)\s+(\w+)\s*\([^)]*\)'
        )
        self._struct_pattern = re.compile(
            r'type\s+(\w+)\s+struct\s*\{'
        )
        self._interface_pattern = re.compile(
            r'type\s+(\w+)\s+interface\s*\{'
        )
        self._import_pattern = re.compile(
            r'import\s+(?:"([^"]+)"|\(\s*([\s\S]*?)\s*\))'
        )
        self._call_pattern = re.compile(r'(\w+)\s*\(')
        
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter()
    
    def _init_tree_sitter(self) -> None:
        """Initialize tree-sitter parser"""
        try:
            self._tree_sitter_parser = get_parser('go')
            LOGGER.info("Go parser initialized with tree-sitter")
        except Exception as e:
            LOGGER.warning(f"Tree-sitter not available for Go: {e}")
            self._tree_sitter_parser = None
    
    def parse(self, file_path: Path) -> ParseResult:
        """Parse Go file"""
        LOGGER.debug(f"Parsing Go file: {file_path}")
        
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
        """Parse using tree-sitter"""
        try:
            tree = self._tree_sitter_parser.parse(bytes(content, 'utf8'))
            self._extract_nodes(tree.root_node, result, content, lines)
        except Exception as e:
            LOGGER.warning(f"Tree-sitter parsing failed: {e}")
            self._parse_with_regex(result, content, lines)
    
    def _extract_nodes(
        self,
        node,
        result: ParseResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Extract nodes from tree-sitter parse tree"""
        node_type = node.type
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        
        if node_type == 'type_declaration':
            for child in node.children:
                if child.type == 'type_spec':
                    name_node = None
                    kind = 'struct'
                    
                    for spec_child in child.children:
                        if spec_child.type == 'identifier':
                            name_node = spec_child
                        elif spec_child.type == 'struct_type':
                            kind = 'struct'
                        elif spec_child.type == 'interface_type':
                            kind = 'interface'
                    
                    if name_node:
                        result.types.append({
                            'name': name_node.text.decode('utf8'),
                            'kind': kind,
                            'start_line': start_line,
                            'end_line': end_line,
                            'flags': 0
                        })
        
        elif node_type == 'function_declaration':
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if name_node:
                result.functions.append({
                    'name': name_node.text.decode('utf8'),
                    'start_line': start_line,
                    'end_line': end_line,
                    'signature': self._extract_signature(lines, start_line),
                    'type_id': None,
                    'calls': []
                })
        
        elif node_type == 'method_declaration':
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            
            if name_node:
                result.functions.append({
                    'name': name_node.text.decode('utf8'),
                    'start_line': start_line,
                    'end_line': end_line,
                    'signature': self._extract_signature(lines, start_line),
                    'type_id': None,
                    'calls': []
                })
        
        elif node_type == 'import_declaration':
            for child in node.children:
                if child.type == 'import_spec':
                    path_node = None
                    for imp_child in child.children:
                        if imp_child.type == 'string':
                            path_node = imp_child
                            break
                    
                    if path_node:
                        result.imports.append({
                            'module_path': path_node.text.decode('utf8').strip('"'),
                            'imported_names': [],
                            'is_wildcard': False
                        })
        
        for child in node.children:
            self._extract_nodes(child, result, content, lines)
    
    def _parse_with_regex(
        self,
        result: ParseResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Fallback regex-based parsing"""
        for match in self._struct_pattern.finditer(content):
            struct_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_matching_brace(content, match.end())
            
            result.types.append({
                'name': struct_name,
                'kind': 'struct',
                'start_line': start_line,
                'end_line': end_line,
                'flags': 0
            })
        
        for match in self._interface_pattern.finditer(content):
            interface_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_matching_brace(content, match.end())
            
            result.types.append({
                'name': interface_name,
                'kind': 'interface',
                'start_line': start_line,
                'end_line': end_line,
                'flags': 0
            })
        
        for match in self._function_pattern.finditer(content):
            func_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_matching_brace(content, match.end())
            
            result.functions.append({
                'name': func_name,
                'start_line': start_line,
                'end_line': end_line,
                'signature': self._extract_signature(lines, start_line),
                'type_id': None,
                'calls': []
            })
        
        for match in self._method_pattern.finditer(content):
            method_name = match.group(1)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_matching_brace(content, match.end())
            
            result.functions.append({
                'name': method_name,
                'start_line': start_line,
                'end_line': end_line,
                'signature': self._extract_signature(lines, start_line),
                'type_id': None,
                'calls': []
            })
        
        for match in self._import_pattern.finditer(content):
            imports = match.group(1) or match.group(2)
            if imports:
                for imp in imports.strip().split('\n'):
                    imp = imp.strip().strip('"')
                    if imp:
                        result.imports.append({
                            'module_path': imp,
                            'imported_names': [],
                            'is_wildcard': False
                        })
        
        self._resolve_calls(result, content)
    
    def _resolve_calls(self, result: ParseResult, content: str) -> None:
        """Resolve function calls"""
        known_functions = {f['name'] for f in result.functions}
        
        for func in result.functions:
            func_start = func['start_line'] - 1
            func_end = func['end_line']
            
            func_content = '\n'.join(content.split('\n')[func_start:func_end])
            
            for match in self._call_pattern.finditer(func_content):
                called_name = match.group(1)
                if called_name in known_functions and called_name != func['name']:
                    result.calls.append({
                        'caller': func['name'],
                        'callee': called_name
                    })
    
    def _find_matching_brace(self, content: str, start: int) -> int:
        """Find matching closing brace"""
        depth = 0
        for i in range(start, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    return content[:i].count('\n') + 1
        return content.count('\n') + 1
    
    def _extract_signature(self, lines: List[str], start_line: int) -> str:
        """Extract function signature"""
        if start_line > len(lines):
            return ""
        
        parts = []
        for i in range(start_line - 1, min(start_line + 5, len(lines))):
            parts.append(lines[i].strip())
            if '{' in lines[i]:
                break
        
        return ' '.join(parts).rstrip('{').strip()


def register_go_parser() -> GoParser:
    """Register Go parser with the global registry"""
    parser = GoParser()
    ParserRegistry.register(parser)
    return parser
