"""
Main Service Module
Orchestrates all components of the Code Knowledge Graph System
"""

import time
import signal
import sys
from pathlib import Path
from typing import Optional
from threading import Thread

from ..core.configuration import CONFIG, LOGGER
from ..database import DATABASE_CONNECTION
from ..parsers import initialize_all_parsers
from ..engine import IncrementalUpdateEngine
from ..llm_service import initialize_llm_service
from ..web_server import create_web_server

from .event_broadcaster import EventBroadcaster


class CodeKnowledgeGraphService:
    """
    Main service that orchestrates all components
    Following first principles: single entry point, clean shutdown
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or CONFIG.project_path
        self.update_engine: Optional[IncrementalUpdateEngine] = None
        self.web_server = None
        self.event_broadcaster: Optional[EventBroadcaster] = None
        self._running = False
        self._monitor_thread: Optional[Thread] = None
    
    def initialize(self) -> None:
        """Initialize all components"""
        LOGGER.info("=" * 60)
        LOGGER.info("Code Knowledge Graph System - Initializing")
        LOGGER.info("=" * 60)
        
        LOGGER.info(f"Project path: {self.project_path}")
        LOGGER.info(f"Database path: {CONFIG.database_path}")
        
        DATABASE_CONNECTION.initialize_database()
        LOGGER.info("Database initialized")
        
        initialize_all_parsers()
        LOGGER.info("Parsers initialized")
        
        if CONFIG.api_key:
            initialize_llm_service(CONFIG.api_key)
            LOGGER.info("LLM service initialized")
        
        self.update_engine = IncrementalUpdateEngine(self.project_path)
        self.update_engine.initialize()
        
        self.event_broadcaster = EventBroadcaster(self.update_engine)
        self.event_broadcaster.start()
        
        self.web_server = create_web_server()
        
        LOGGER.info("All components initialized successfully")
        LOGGER.info("=" * 60)
    
    def run_full_sync(self) -> None:
        """Run full synchronization"""
        LOGGER.info("Starting full synchronization...")
        start_time = time.time()
        
        stats = self.update_engine.full_sync()
        
        elapsed = time.time() - start_time
        LOGGER.info(f"Full sync completed in {elapsed:.2f}s")
        LOGGER.info(f"  Files processed: {stats.files_processed}")
        LOGGER.info(f"  Files created: {stats.files_created}")
        LOGGER.info(f"  Files updated: {stats.files_updated}")
        LOGGER.info(f"  Files deleted: {stats.files_deleted}")
        LOGGER.info(f"  Types processed: {stats.types_processed}")
        LOGGER.info(f"  Functions processed: {stats.functions_processed}")
        if stats.errors:
            LOGGER.warning(f"  Errors: {len(stats.errors)}")
            for error in stats.errors[:5]:
                LOGGER.warning(f"    - {error}")
        
        self.web_server.emit_stats_update()
    
    def start_monitoring(self) -> None:
        """Start file monitoring"""
        LOGGER.info("Starting file monitoring...")
        self.update_engine.start_monitoring()
        self._running = True
        LOGGER.info("File monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop file monitoring"""
        LOGGER.info("Stopping file monitoring...")
        self._running = False
        if self.update_engine:
            self.update_engine.stop_monitoring()
        if self.event_broadcaster:
            self.event_broadcaster.stop()
        LOGGER.info("File monitoring stopped")
    
    def run_web_server(self) -> None:
        """Run the web server (blocking)"""
        LOGGER.info("Starting web server...")
        self.web_server.run()
    
    def run(self) -> None:
        """Run the complete service"""
        self.initialize()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.run_full_sync()
        
        self.start_monitoring()
        
        try:
            self.run_web_server()
        except KeyboardInterrupt:
            LOGGER.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        LOGGER.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self) -> None:
        """Clean shutdown"""
        LOGGER.info("Shutting down Code Knowledge Graph System...")
        
        self.stop_monitoring()
        
        DATABASE_CONNECTION.close()
        
        LOGGER.info("Shutdown complete")


def create_service(project_path: Optional[Path] = None) -> CodeKnowledgeGraphService:
    """Factory function to create the service"""
    return CodeKnowledgeGraphService(project_path)
