"""
Universal Parser Interface Module
Defines the contract for all language parsers following first principles
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import os

from ..core.configuration import LOGGER


@dataclass
class ParseResult:
    """Universal parse result format for all languages"""
    file_path: str
    language: str
    file_hash: bytes
    modified_time: int
    types: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    calls: List[Dict[str, Any]] = field(default_factory=list)
    references: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if parse result has any content"""
        return bool(self.types or self.functions or self.calls)


@dataclass
class TypeInfo:
    """Type information structure"""
    name: str
    kind: str
    start_line: int
    end_line: int
    flags: int = 0
    docstring: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)


@dataclass
class FunctionInfo:
    """Function information structure"""
    name: str
    start_line: int
    end_line: int
    signature: str
    type_id: Optional[int] = None
    docstring: Optional[str] = None
    calls: List[str] = field(default_factory=list)


class UniversalParser(ABC):
    """
    Abstract base class for all language parsers
    Following first principles: all parsers must implement the same interface
    """
    
    LANGUAGE_NAME: str = "unknown"
    FILE_EXTENSIONS: tuple = ()
    
    @abstractmethod
    def parse(self, file_path: Path) -> ParseResult:
        """Parse a file and return universal parse result"""
        pass
    
    @abstractmethod
    def get_language(self) -> str:
        """Get the language name for this parser"""
        pass
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file"""
        return file_path.suffix.lower() in self.FILE_EXTENSIONS
    
    def compute_file_hash(self, file_path: Path) -> bytes:
        """Compute MD5 hash of file content"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.digest()
    
    def get_modified_time(self, file_path: Path) -> int:
        """Get file modification time as Unix timestamp"""
        return int(file_path.stat().st_mtime)
    
    def read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Unable to decode file: {file_path}")


class ParserRegistry:
    """Registry for all language parsers"""
    
    _parsers: Dict[str, UniversalParser] = {}
    _extension_map: Dict[str, str] = {}
    
    @classmethod
    def register(cls, parser: UniversalParser) -> None:
        """Register a parser"""
        cls._parsers[parser.LANGUAGE_NAME] = parser
        for ext in parser.FILE_EXTENSIONS:
            cls._extension_map[ext.lower()] = parser.LANGUAGE_NAME
        LOGGER.info(f"Registered parser: {parser.LANGUAGE_NAME}")
    
    @classmethod
    def get_parser(cls, language: str) -> Optional[UniversalParser]:
        """Get parser by language name"""
        return cls._parsers.get(language)
    
    @classmethod
    def get_parser_for_file(cls, file_path: Path) -> Optional[UniversalParser]:
        """Get appropriate parser for a file based on extension"""
        ext = file_path.suffix.lower()
        language = cls._extension_map.get(ext)
        if language:
            return cls._parsers.get(language)
        return None
    
    @classmethod
    def get_language_for_extension(cls, extension: str) -> Optional[str]:
        """Get language name for file extension"""
        return cls._extension_map.get(extension.lower())
    
    @classmethod
    def get_all_parsers(cls) -> Dict[str, UniversalParser]:
        """Get all registered parsers"""
        return cls._parsers.copy()
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get all supported file extensions"""
        return list(cls._extension_map.keys())


def detect_language(file_path: Path) -> Optional[str]:
    """Detect language from file extension"""
    return ParserRegistry.get_language_for_extension(file_path.suffix)


def create_parser_for_language(language: str) -> Optional[UniversalParser]:
    """Factory function to create parser for a language"""
    return ParserRegistry.get_parser(language)
