"""System configuration module"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SystemConfiguration:
    """System configuration with default values following first principles"""
    project_path: Path = field(default_factory=lambda: Path.cwd())
    database_path: Path = field(default_factory=lambda: Path("code_knowledge.db"))
    debounce_window_ms: int = 1000
    max_workers: int = 4
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    api_base_url: str = "https://api.siliconflow.cn/v1"
    api_key: str = ""
    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8080
    supported_languages: tuple = (
        ".py", ".java", ".js", ".ts", ".tsx", ".jsx",
        ".go", ".rs", ".cpp", ".c", ".h", ".hpp",
        ".cs", ".rb", ".swift", ".kt", ".scala",
        ".ets", ".ts"
    )


def load_configuration() -> SystemConfiguration:
    """Load configuration from environment or defaults"""
    config = SystemConfiguration()
    
    if os.getenv("PROJECT_PATH"):
        config.project_path = Path(os.getenv("PROJECT_PATH"))
    if os.getenv("DATABASE_PATH"):
        config.database_path = Path(os.getenv("DATABASE_PATH"))
    if os.getenv("DEBOUNCE_WINDOW_MS"):
        config.debounce_window_ms = int(os.getenv("DEBOUNCE_WINDOW_MS"))
    if os.getenv("API_KEY"):
        config.api_key = os.getenv("API_KEY")
    if os.getenv("LOG_LEVEL"):
        config.log_level = os.getenv("LOG_LEVEL")
    
    return config


def setup_logging(config: SystemConfiguration) -> logging.Logger:
    """Setup logging following first principles - minimal, focused output"""
    logger = logging.getLogger("code_knowledge_graph")
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


CONFIG = load_configuration()
LOGGER = setup_logging(CONFIG)
