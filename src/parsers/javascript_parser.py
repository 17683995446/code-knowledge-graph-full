"""
JavaScript/TypeScript Parser Module
Using tree-sitter for accurate JavaScript and TypeScript parsing
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


class JavaScriptParser(UniversalParser):
    """
    JavaScript parser supporting .js and .jsx files
    Uses tree-sitter when available
    """
    
    LANGUAGE_NAME = "javascript"
    FILE_EXTENSIONS = ('.js', '.jsx')
    
    def __init__(self):
        self._tree_sitter_parser = None
        self._function_pattern = re.compile(
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)'
        )
        self._arrow_pattern = re.compile(
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'
        )
        self._class_pattern = re.compile(
            r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        )
        self._import_pattern = re.compile(
            r'import\s+(?:'
            r'\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]|'
            r'([\w*]+)\s+from\s+[\'"]([^\'"]+)[\'"]|'
            r'([\w*]+)\s+as\s+\w+\s+from\s+[\'"]([^\'"]+)[\'"]|'
            r'[\'"]([^\'"]+)[\'"]'
            r')'
        )
        self._call_pattern = re.compile(r'(\w+)\s*\(')
        
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter()
    
    def _init_tree_sitter(self) -> None:
        """Initialize tree-sitter parser"""
        try:
            self._tree_sitter_parser = get_parser('javascript')
            LOGGER.info("JavaScript parser initialized with tree-sitter")
        except Exception as e:
            LOGGER.warning(f"Tree-sitter not available for JavaScript: {e}")
            self._tree_sitter_parser = None
    
    def parse(self, file_path: Path) -> ParseResult:
        """Parse JavaScript file"""
        LOGGER.debug(f"Parsing JavaScript file: {file_path}")
        
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
        
        if node_type == 'class_declaration':
            name_node = None
            super_class = None
            
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                elif child.type == 'extends_clause':
                    for ext_child in child.children:
                        if ext_child.type == 'identifier':
                            super_class = ext_child.text.decode('utf8')
                            break
            
            if name_node:
                result.types.append({
                    'name': name_node.text.decode('utf8'),
                    'kind': 'class',
                    'start_line': start_line,
                    'end_line': end_line,
                    'flags': 0,
                    'base_classes': [super_class] if super_class else []
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
        
        elif node_type == 'import_statement':
            source = None
            names = []
            
            for child in node.children:
                if child.type == 'string':
                    source = child.text.decode('utf8').strip('"\'')
                elif child.type == 'import_clause':
                    for imp_child in child.children:
                        if imp_child.type == 'identifier':
                            names.append(imp_child.text.decode('utf8'))
                        elif imp_child.type == 'import_specifier':
                            for spec_child in imp_child.children:
                                if spec_child.type == 'identifier':
                                    names.append(spec_child.text.decode('utf8'))
            
            if source:
                result.imports.append({
                    'module_path': source,
                    'imported_names': names,
                    'is_wildcard': '*' in names
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
        for match in self._class_pattern.finditer(content):
            class_name = match.group(1)
            base_class = match.group(2)
            start_line = content[:match.start()].count('\n') + 1
            end_line = self._find_matching_brace(content, match.end())
            
            result.types.append({
                'name': class_name,
                'kind': 'class',
                'start_line': start_line,
                'end_line': end_line,
                'flags': 0,
                'base_classes': [base_class] if base_class else []
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
        
        for match in self._import_pattern.finditer(content):
            group1 = match.group(1)
            group2 = match.group(2)
            group3 = match.group(3)
            group4 = match.group(4)
            group5 = match.group(5)
            group6 = match.group(6)
            group7 = match.group(7)
            
            if group1 and group2:
                # Named import: import { A, B } from 'module'
                names = [n.strip() for n in group1.split(',') if n.strip()]
                result.imports.append({
                    'module_path': group2,
                    'imported_names': names,
                    'is_wildcard': False
                })
            elif group3 and group4:
                # Default import: import A from 'module'
                result.imports.append({
                    'module_path': group4,
                    'imported_names': [group3],
                    'is_wildcard': '*' == group3
                })
            elif group5 and group6:
                # Wildcard import: import * as All from 'module'
                result.imports.append({
                    'module_path': group6,
                    'imported_names': [],
                    'is_wildcard': True
                })
            elif group7:
                # Side-effect import: import 'module'
                result.imports.append({
                    'module_path': group7,
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


class TypeScriptParser(JavaScriptParser):
    """
    TypeScript parser supporting .ts and .tsx files
    Extends JavaScript parser with TypeScript-specific features
    """
    
    LANGUAGE_NAME = "typescript"
    FILE_EXTENSIONS = ('.ts', '.tsx')
    
    def get_language(self) -> str:
        """Get language name"""
        return self.LANGUAGE_NAME


def register_javascript_parser() -> JavaScriptParser:
    """Register JavaScript parser with the global registry"""
    parser = JavaScriptParser()
    ParserRegistry.register(parser)
    return parser


def register_typescript_parser() -> TypeScriptParser:
    """Register TypeScript parser with the global registry"""
    parser = TypeScriptParser()
    ParserRegistry.register(parser)
    return parser
