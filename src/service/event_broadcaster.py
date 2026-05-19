"""
Event Broadcaster Module
Broadcasts file change events to WebSocket clients
"""

import time
from typing import Optional

from ..core.configuration import LOGGER
from ..web_server import get_web_server


class EventBroadcaster:
    """
    Broadcasts update events to connected WebSocket clients
    Following first principles: decouple processing from notification
    """
    
    def __init__(self, update_engine):
        self.update_engine = update_engine
        self._running = False
        self._last_stats = {}
        self._poll_interval = 2
    
    def start(self) -> None:
        """Start broadcasting"""
        self._running = True
        LOGGER.info("Event broadcaster started")
    
    def stop(self) -> None:
        """Stop broadcasting"""
        self._running = False
        LOGGER.info("Event broadcaster stopped")
    
    def broadcast_stats_update(self) -> None:
        """Broadcast statistics update to all clients"""
        web_server = get_web_server()
        if web_server:
            stats = self.update_engine.get_statistics()
            web_server.emit_stats_update()
    
    def broadcast_file_event(self, event_type: str, file_path: str) -> None:
        """Broadcast file event to all clients"""
        web_server = get_web_server()
        if web_server:
            web_server.emit_update(event_type, {
                'path': file_path,
                'timestamp': int(time.time())
            })
    
    def broadcast_sync_complete(self) -> None:
        """Broadcast sync completion event"""
        web_server = get_web_server()
        if web_server:
            stats = self.update_engine.get_statistics()
            web_server.emit_update('sync_complete', {
                'stats': stats,
                'timestamp': int(time.time())
            })
