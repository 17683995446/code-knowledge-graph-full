"""
Database Connection Manager Module
Provides centralized SQLite database connection management following first principles
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass

from ..core.configuration import CONFIG, LOGGER

@dataclass
class DatabaseSchema:
    """Database schema definitions following universal data model"""
    
    @staticmethod
    def get_create_tables_sql() -> List[str]:
        """Get SQL statements for creating all required tables"""
        return [
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                language TEXT NOT NULL,
                hash BLOB NOT NULL,
                modified INTEGER NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                flags INTEGER DEFAULT 0,
                start_line INTEGER,
                end_line INTEGER,
                docstring TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                UNIQUE(name, file_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS functions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type_id INTEGER,
                file_id INTEGER NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                signature TEXT,
                docstring TEXT,
                FOREIGN KEY (type_id) REFERENCES types(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                UNIQUE(name, type_id, file_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS calls (
                caller_id INTEGER NOT NULL,
                callee_id INTEGER NOT NULL,
                call_type TEXT DEFAULT 'direct',
                PRIMARY KEY (caller_id, callee_id),
                FOREIGN KEY (caller_id) REFERENCES functions(id) ON DELETE CASCADE,
                FOREIGN KEY (callee_id) REFERENCES functions(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS references_table (
                from_id INTEGER NOT NULL,
                to_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                PRIMARY KEY (from_id, to_id, kind),
                FOREIGN KEY (from_id) REFERENCES types(id) ON DELETE CASCADE,
                FOREIGN KEY (to_id) REFERENCES types(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS import_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                module_path TEXT NOT NULL,
                imported_names TEXT,
                is_wildcard INTEGER DEFAULT 0,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_files_language ON files(language);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_types_file ON types(file_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_types_name ON types(name);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_functions_file ON functions(file_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_functions_type ON functions(type_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_references_from ON references_table(from_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_references_to ON references_table(to_id);
            """
        ]


class DatabaseConnection:
    """Thread-safe SQLite database connection manager"""
    
    _local = threading.local()
    _lock = threading.Lock()
    
    def __init__(self, database_path: Optional[Path] = None):
        self.database_path = database_path or CONFIG.database_path
        self._initialized = False
    
    def _get_connection(self, already_locked: bool = False) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            if already_locked:
                # We already hold the lock, don't try to acquire it again
                self._create_connection()
            else:
                with self._lock:
                    # Double-check after acquiring lock
                    if not hasattr(self._local, 'connection') or self._local.connection is None:
                        self._create_connection()
        return self._local.connection
    
    def _create_connection(self) -> None:
        """Create database connection (must be called with lock held if necessary)"""
        self._local.connection = sqlite3.connect(
            str(self.database_path),
            check_same_thread=False,
            timeout=60.0
        )
        self._local.connection.row_factory = sqlite3.Row
        try:
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            self._local.connection.execute("PRAGMA journal_mode = WAL")
            self._local.connection.execute("PRAGMA synchronous = NORMAL")
            self._local.connection.execute("PRAGMA cache_size = -64000")
            self._local.connection.execute("PRAGMA temp_store = MEMORY")
            self._local.connection.execute("PRAGMA busy_timeout = 30000")
        except sqlite3.OperationalError as e:
            LOGGER.warning(f"Could not set some SQLite pragmas: {e}")
    
    @contextmanager
    def get_cursor(self, already_locked: bool = False):
        """Context manager for database cursor with automatic commit/rollback"""
        conn = self._get_connection(already_locked=already_locked)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            LOGGER.error(f"Database transaction failed: {e}")
            raise
        finally:
            cursor.close()
    
    def initialize_database(self) -> None:
        """Initialize database schema"""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            LOGGER.info(f"Initializing database at {self.database_path}")
            
            with self.get_cursor(already_locked=True) as cursor:
                for sql in DatabaseSchema.get_create_tables_sql():
                    cursor.executescript(sql)
            
            self._initialized = True
            LOGGER.info("Database initialized successfully")
    
    def close(self) -> None:
        """Close thread-local database connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def vacuum(self) -> None:
        """Optimize database by running VACUUM"""
        LOGGER.info("Running database VACUUM for optimization")
        with self.get_cursor() as cursor:
            cursor.execute("VACUUM")
        LOGGER.info("Database VACUUM completed")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        with self.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM files")
            stats['total_files'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM types")
            stats['total_types'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM functions")
            stats['total_functions'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM calls")
            stats['total_calls'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM references_table")
            stats['total_references'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT language, COUNT(*) as count 
                FROM files GROUP BY language ORDER BY count DESC
            """)
            stats['files_by_language'] = [
                {'language': row['language'], 'count': row['count']}
                for row in cursor.fetchall()
            ]
            
            cursor.execute("""
                SELECT kind, COUNT(*) as count 
                FROM types GROUP BY kind ORDER BY count DESC
            """)
            stats['types_by_kind'] = [
                {'kind': row['kind'], 'count': row['count']}
                for row in cursor.fetchall()
            ]
            
            db_path = Path(self.database_path)
            if db_path.exists():
                stats['database_size_bytes'] = db_path.stat().st_size
                stats['database_size_mb'] = round(db_path.stat().st_size / (1024 * 1024), 2)
        
        return stats


DATABASE_CONNECTION = DatabaseConnection()
