"""
File Monitor Module
Cross-platform file system monitoring with debouncing
"""

import os
import time
import threading
from pathlib import Path
from typing import Callable, Set, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty

from ..core.configuration import CONFIG, LOGGER


class FileEventType(Enum):
    """File event types"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileEvent:
    """File system event"""
    event_type: FileEventType
    file_path: Path
    timestamp: float = field(default_factory=time.time)
    
    def __hash__(self):
        return hash((self.event_type, str(self.file_path)))


class DebounceQueue:
    """
    Debounce queue to merge rapid file changes
    Following first principles: user modifications should be debounced
    """
    
    def __init__(self, debounce_ms: int = 1000):
        self._debounce_ms = debounce_ms
        self._queue: Queue = Queue()
        self._pending: Dict[str, FileEvent] = {}
        self._lock = threading.Lock()
        self._last_flush = time.time()
    
    def put(self, event: FileEvent) -> None:
        """Add event to queue, merging duplicates"""
        key = str(event.file_path)
        
        with self._lock:
            self._pending[key] = event
            LOGGER.debug(f"Event queued: {event.event_type.value} {event.file_path}")
    
    def get_batch(self, timeout_ms: int = 100) -> List[FileEvent]:
        """Get batch of events after debounce window"""
        current_time = time.time()
        elapsed_ms = (current_time - self._last_flush) * 1000
        
        if elapsed_ms < self._debounce_ms and not self._queue.empty():
            return []
        
        with self._lock:
            if not self._pending:
                return []
            
            events = list(self._pending.values())
            self._pending.clear()
            self._last_flush = current_time
            
            LOGGER.debug(f"Flushing {len(events)} events after {elapsed_ms:.0f}ms")
            return events


class FileMonitor:
    """
    Cross-platform file system monitor
    Supports both inotify (Linux) and polling (cross-platform fallback)
    """
    
    def __init__(
        self,
        project_path: Path,
        extensions: tuple = CONFIG.supported_languages,
        debounce_ms: int = CONFIG.debounce_window_ms
    ):
        self.project_path = project_path
        self.extensions = set(extensions)
        self.debounce_ms = debounce_ms
        
        self._callbacks: List[Callable[[List[FileEvent]], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._debounce_queue = DebounceQueue(debounce_ms)
        
        self._watcher = None
        self._use_inotify = False
        
        self._init_watcher()
    
    def _init_watcher(self) -> None:
        """Initialize appropriate file watcher"""
        if os.name == 'posix' and hasattr(os, 'inotify_init'):
            try:
                import inotify.adapters
                self._watcher = inotify.adapters.Inotify()
                self._use_inotify = True
                LOGGER.info("Using inotify for file monitoring (Linux)")
            except Exception as e:
                LOGGER.warning(f"Inotify not available: {e}, using polling")
                self._use_inotify = False
        else:
            LOGGER.info("Using polling for file monitoring")
            self._use_inotify = False
        
        if not self._use_inotify:
            self._file_mtimes: Dict[str, float] = {}
            self._scan_initial_state()
    
    def _scan_initial_state(self) -> None:
        """Scan initial file state for polling mode"""
        LOGGER.info("Scanning initial file state...")
        
        for ext in self.extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if self._is_valid_file(file_path):
                    try:
                        self._file_mtimes[str(file_path)] = file_path.stat().st_mtime
                    except OSError:
                        pass
        
        LOGGER.info(f"Initial scan complete: {len(self._file_mtimes)} files tracked")
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """Check if file should be monitored"""
        if not file_path.is_file():
            return False
        
        if file_path.suffix.lower() not in self.extensions:
            return False
        
        path_str = str(file_path)
        
        invalid_patterns = [
            '__pycache__', '.pytest_cache', '.mypy_cache',
            'node_modules', '.git', '.svn', '.hg',
            'venv', '.venv', 'env', '.env',
            '.tox', '.eggs', 'build', 'dist', '.eggs',
            '.hypothesis', '.nox', '.pytest_cache',
            '.cache', '.DS_Store', 'Thumbs.db',
        ]
        
        for pattern in invalid_patterns:
            if pattern in path_str:
                return False
        
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        return True
    
    def register_callback(self, callback: Callable[[List[FileEvent]], None]) -> None:
        """Register callback for file events"""
        self._callbacks.append(callback)
    
    def start(self) -> None:
        """Start file monitoring"""
        if self._running:
            LOGGER.warning("File monitor already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        LOGGER.info(f"File monitor started for {self.project_path}")
    
    def stop(self) -> None:
        """Stop file monitoring"""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        
        if self._watcher and self._use_inotify:
            try:
                self._watcher.close()
            except Exception:
                pass
        
        LOGGER.info("File monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        if self._use_inotify:
            self._inotify_loop()
        else:
            self._polling_loop()
    
    def _inotify_loop(self) -> None:
        """Linux inotify-based monitoring loop"""
        import inotify.adapters
        
        mask = (
            inotify.adapters.IN_MODIFY |
            inotify.adapters.IN_CREATE |
            inotify.adapters.IN_DELETE |
            inotify.adapters.IN_MOVED_FROM |
            inotify.adapters.IN_MOVED_TO
        )
        
        self._watcher.add_watch(str(self.project_path), mask, recursive=True)
        
        while self._running:
            try:
                events = self._watcher.event_gen(timeout_s=1)
                if events:
                    for event in events:
                        if not self._running:
                            break
                        
                        if event is None:
                            continue
                        
                        event_type, event_path, event_cookie = event
                        
                        file_path = Path(event_path)
                        if not self._is_valid_file(file_path):
                            continue
                        
                        if 'IN_ISDIR' in event_type:
                            continue
                        
                        if 'CREATE' in event_type or 'MODIFY' in event_type:
                            self._debounce_queue.put(
                                FileEvent(FileEventType.CREATED if 'CREATE' in event_type else FileEventType.MODIFIED, file_path)
                            )
                        elif 'DELETE' in event_type or 'MOVED_FROM' in event_type:
                            self._debounce_queue.put(
                                FileEvent(FileEventType.DELETED, file_path)
                            )
                        elif 'MOVED_TO' in event_type:
                            self._debounce_queue.put(
                                FileEvent(FileEventType.CREATED, file_path)
                            )
                
                self._flush_events()
                
            except Exception as e:
                LOGGER.error(f"Error in inotify loop: {e}")
                time.sleep(1)
    
    def _polling_loop(self) -> None:
        """Cross-platform polling-based monitoring loop"""
        while self._running:
            try:
                current_files: Set[str] = set()
                new_events: List[FileEvent] = []
                
                for ext in self.extensions:
                    for file_path in self.project_path.rglob(f"*{ext}"):
                        if not self._is_valid_file(file_path):
                            continue
                        
                        path_str = str(file_path)
                        current_files.add(path_str)
                        
                        try:
                            current_mtime = file_path.stat().st_mtime
                        except OSError:
                            continue
                        
                        if path_str not in self._file_mtimes:
                            new_events.append(
                                FileEvent(FileEventType.CREATED, file_path)
                            )
                            self._file_mtimes[path_str] = current_mtime
                        elif current_mtime > self._file_mtimes[path_str]:
                            new_events.append(
                                FileEvent(FileEventType.MODIFIED, file_path)
                            )
                            self._file_mtimes[path_str] = current_mtime
                
                deleted_files = set(self._file_mtimes.keys()) - current_files
                for path_str in deleted_files:
                    new_events.append(
                        FileEvent(FileEventType.DELETED, Path(path_str))
                    )
                    del self._file_mtimes[path_str]
                
                for event in new_events:
                    self._debounce_queue.put(event)
                
                self._flush_events()
                time.sleep(1)
                
            except Exception as e:
                LOGGER.error(f"Error in polling loop: {e}")
                time.sleep(1)
    
    def _flush_events(self) -> None:
        """Flush debounced events to callbacks"""
        events = self._debounce_queue.get_batch()
        
        if events:
            LOGGER.info(f"Flushing {len(events)} file events")
            for callback in self._callbacks:
                try:
                    callback(events)
                except Exception as e:
                    LOGGER.error(f"Callback error: {e}")
    
    def scan_all_files(self) -> List[Path]:
        """Scan all monitored files"""
        files = []
        
        for ext in self.extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if self._is_valid_file(file_path):
                    files.append(file_path)
        
        return files


def create_file_monitor(
    project_path: Optional[Path] = None,
    extensions: Optional[tuple] = None
) -> FileMonitor:
    """Factory function to create file monitor"""
    return FileMonitor(
        project_path=project_path or CONFIG.project_path,
        extensions=extensions or CONFIG.supported_languages
    )
