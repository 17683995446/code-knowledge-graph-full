#!/usr/bin/env python3
"""
Code Knowledge Graph System - Main Entry Point
Universal Programming Language Code Knowledge Graph System

Usage:
    python -m src.main --project-path /path/to/project
    python -m src.main --full-sync
    python -m src.main --web-only
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.configuration import CONFIG, LOGGER
from src.service import create_service


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Code Knowledge Graph System - Universal code analysis tool'
    )
    
    parser.add_argument(
        '--project-path',
        type=Path,
        default=CONFIG.project_path,
        help='Path to the project to analyze'
    )
    
    parser.add_argument(
        '--database-path',
        type=Path,
        default=CONFIG.database_path,
        help='Path to SQLite database'
    )
    
    parser.add_argument(
        '--debounce-window',
        type=int,
        default=CONFIG.debounce_window_ms,
        help='Debounce window in milliseconds'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        default=CONFIG.api_key,
        help='Silicon Flow API key for LLM'
    )
    
    parser.add_argument(
        '--web-host',
        type=str,
        default=CONFIG.web_server_host,
        help='Web server host'
    )
    
    parser.add_argument(
        '--web-port',
        type=int,
        default=CONFIG.web_server_port,
        help='Web server port'
    )
    
    parser.add_argument(
        '--full-sync',
        action='store_true',
        help='Run full synchronization and exit'
    )
    
    parser.add_argument(
        '--web-only',
        action='store_true',
        help='Start web server only (no monitoring)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default=CONFIG.log_level,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    return parser.parse_args()


def update_config(args):
    """Update configuration from arguments"""
    if args.project_path:
        CONFIG.project_path = args.project_path
    if args.database_path:
        CONFIG.database_path = args.database_path
    if args.debounce_window:
        CONFIG.debounce_window_ms = args.debounce_window
    if args.api_key:
        CONFIG.api_key = args.api_key
    if args.web_host:
        CONFIG.web_server_host = args.web_host
    if args.web_port:
        CONFIG.web_server_port = args.web_port
    if args.log_level:
        CONFIG.log_level = args.log_level


def main():
    """Main entry point"""
    args = parse_arguments()
    update_config(args)
    
    LOGGER.info("Code Knowledge Graph System v1.0.0")
    LOGGER.info("Universal Programming Language Code Analysis")
    LOGGER.info("=" * 50)
    
    if args.web_only:
        from src.web_server import create_web_server
        web_server = create_web_server()
        web_server.run()
        return
    
    service = create_service(args.project_path)
    
    if args.full_sync:
        service.initialize()
        service.run_full_sync()
        service.shutdown()
        return
    
    service.run()


if __name__ == '__main__':
    main()
