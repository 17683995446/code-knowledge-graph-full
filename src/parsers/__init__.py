"""
Parser Module Initialization
Registers all available parsers
"""

from ..core.configuration import LOGGER
from .universal_parser import (
    UniversalParser,
    ParseResult,
    ParserRegistry,
    detect_language,
    create_parser_for_language
)
from .arkts_parser import ArkAnalyzerParser, register_arkts_parser
from .python_parser import PythonParser, register_python_parser
from .javascript_parser import (
    JavaScriptParser,
    TypeScriptParser,
    register_javascript_parser,
    register_typescript_parser
)
from .go_parser import GoParser, register_go_parser


def initialize_all_parsers() -> None:
    """Initialize and register all available parsers"""
    LOGGER.info("Initializing all language parsers...")
    
    register_python_parser()
    register_javascript_parser()
    register_typescript_parser()
    register_arkts_parser()
    register_go_parser()
    
    LOGGER.info(
        f"Registered {len(ParserRegistry.get_all_parsers())} parsers: "
        f"{', '.join(ParserRegistry.get_all_parsers().keys())}"
    )


def get_parser_for_file(file_path):
    """Get appropriate parser for a file"""
    return ParserRegistry.get_parser_for_file(file_path)


__all__ = [
    'UniversalParser',
    'ParseResult',
    'ParserRegistry',
    'ArkAnalyzerParser',
    'PythonParser',
    'JavaScriptParser',
    'TypeScriptParser',
    'GoParser',
    'register_arkts_parser',
    'register_python_parser',
    'register_javascript_parser',
    'register_typescript_parser',
    'register_go_parser',
    'initialize_all_parsers',
    'detect_language',
    'create_parser_for_language',
    'get_parser_for_file',
]
