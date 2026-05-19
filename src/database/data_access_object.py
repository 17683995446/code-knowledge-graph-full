"""
Data Access Object Module
Provides CRUD operations for all database entities following first principles
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import hashlib

from .database_connection import DATABASE_CONNECTION, DatabaseConnection

from ..core.configuration import LOGGER


@dataclass
class FileEntity:
    """File entity representation"""
    path: str
    language: str
    hash: bytes
    modified: int


@dataclass
class TypeEntity:
    """Type entity representation (class, interface, struct, enum, etc.)"""
    name: str
    file_id: int
    kind: str
    flags: int = 0
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    docstring: Optional[str] = None


@dataclass
class FunctionEntity:
    """Function entity representation"""
    name: str
    type_id: Optional[int]
    file_id: int
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None


@dataclass
class CallRelationship:
    """Call relationship between functions"""
    caller_id: int
    callee_id: int
    call_type: str = "direct"


@dataclass
class ReferenceRelationship:
    """Reference relationship between types"""
    from_id: int
    to_id: int
    kind: str


class FileDAO:
    """Data Access Object for file operations"""
    
    @staticmethod
    def create(file_entity: FileEntity) -> int:
        """Create a new file record"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO files (path, language, hash, modified)
                VALUES (?, ?, ?, ?)
            """, (file_entity.path, file_entity.language, file_entity.hash, file_entity.modified))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_path(path: str) -> Optional[Dict[str, Any]]:
        """Get file by path"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_id(file_id: int) -> Optional[Dict[str, Any]]:
        """Get file by ID"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all files"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM files ORDER BY path")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_hash(file_id: int, hash_value: bytes, modified: int) -> None:
        """Update file hash and modification time"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                UPDATE files 
                SET hash = ?, modified = ?, updated_at = strftime('%s', 'now')
                WHERE id = ?
            """, (hash_value, modified, file_id))
    
    @staticmethod
    def delete_by_path(path: str) -> bool:
        """Delete file by path (cascades to related entities)"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM files WHERE path = ?", (path,))
            return cursor.rowcount > 0
    
    @staticmethod
    def delete_by_id(file_id: int) -> bool:
        """Delete file by ID (cascades to related entities)"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def get_by_language(language: str) -> List[Dict[str, Any]]:
        """Get all files of a specific language"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM files WHERE language = ? ORDER BY path", (language,))
            return [dict(row) for row in cursor.fetchall()]


class TypeDAO:
    """Data Access Object for type operations"""
    
    @staticmethod
    def create(type_entity: TypeEntity) -> int:
        """Create a new type record"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO types (name, file_id, kind, flags, start_line, end_line, docstring)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                type_entity.name,
                type_entity.file_id,
                type_entity.kind,
                type_entity.flags,
                type_entity.start_line,
                type_entity.end_line,
                type_entity.docstring
            ))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_name_and_file(name: str, file_id: int) -> Optional[Dict[str, Any]]:
        """Get type by name and file ID"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM types WHERE name = ? AND file_id = ?
            """, (name, file_id))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_file(file_id: int) -> List[Dict[str, Any]]:
        """Get all types in a file"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM types WHERE file_id = ? ORDER BY start_line", (file_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_by_file(file_id: int) -> int:
        """Delete all types in a file"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM types WHERE file_id = ?", (file_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all types"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT t.*, f.path as file_path, f.language
                FROM types t
                JOIN files f ON t.file_id = f.id
                ORDER BY t.name
            """)
            return [dict(row) for row in cursor.fetchall()]


class FunctionDAO:
    """Data Access Object for function operations"""
    
    @staticmethod
    def create(function_entity: FunctionEntity) -> int:
        """Create a new function record"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO functions (name, type_id, file_id, start_line, end_line, signature, docstring)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                function_entity.name,
                function_entity.type_id,
                function_entity.file_id,
                function_entity.start_line,
                function_entity.end_line,
                function_entity.signature,
                function_entity.docstring
            ))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_name_and_type(name: str, type_id: Optional[int], file_id: int) -> Optional[Dict[str, Any]]:
        """Get function by name, type_id, and file_id"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM functions 
                WHERE name = ? AND type_id IS ? AND file_id = ?
            """, (name, type_id, file_id))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_file(file_id: int) -> List[Dict[str, Any]]:
        """Get all functions in a file"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, t.name as type_name
                FROM functions f
                LEFT JOIN types t ON f.type_id = t.id
                WHERE f.file_id = ?
                ORDER BY f.start_line
            """, (file_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_type(type_id: int) -> List[Dict[str, Any]]:
        """Get all functions in a type"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("SELECT * FROM functions WHERE type_id = ? ORDER BY start_line", (type_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_by_file(file_id: int) -> int:
        """Delete all functions in a file"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM functions WHERE file_id = ?", (file_id,))
            return cursor.rowcount
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all functions"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT fn.*, f.path as file_path, t.name as type_name
                FROM functions fn
                JOIN files f ON fn.file_id = f.id
                LEFT JOIN types t ON fn.type_id = t.id
                ORDER BY fn.name
            """)
            return [dict(row) for row in cursor.fetchall()]


class CallDAO:
    """Data Access Object for call relationships"""
    
    @staticmethod
    def create(call_relationship: CallRelationship) -> bool:
        """Create a call relationship"""
        try:
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR IGNORE INTO calls (caller_id, callee_id, call_type)
                    VALUES (?, ?, ?)
                """, (call_relationship.caller_id, call_relationship.callee_id, call_relationship.call_type))
                return cursor.rowcount > 0
        except Exception as e:
            LOGGER.warning(f"Failed to create call relationship: {e}")
            return False
    
    @staticmethod
    def get_callers(function_id: int) -> List[Dict[str, Any]]:
        """Get all functions that call the given function"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, c.call_type
                FROM calls c
                JOIN functions f ON c.caller_id = f.id
                WHERE c.callee_id = ?
            """, (function_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_callees(function_id: int) -> List[Dict[str, Any]]:
        """Get all functions called by the given function"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT f.*, c.call_type
                FROM calls c
                JOIN functions f ON c.callee_id = f.id
                WHERE c.caller_id = ?
            """, (function_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_by_caller(caller_id: int) -> int:
        """Delete all calls made by a function"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM calls WHERE caller_id = ?", (caller_id,))
            return cursor.rowcount
    
    @staticmethod
    def delete_by_callee(callee_id: int) -> int:
        """Delete all calls to a function"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM calls WHERE callee_id = ?", (callee_id,))
            return cursor.rowcount


class ReferenceDAO:
    """Data Access Object for reference relationships"""
    
    @staticmethod
    def create(reference_relationship: ReferenceRelationship) -> bool:
        """Create a reference relationship"""
        try:
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    INSERT OR IGNORE INTO references_table (from_id, to_id, kind)
                    VALUES (?, ?, ?)
                """, (reference_relationship.from_id, reference_relationship.to_id, reference_relationship.kind))
                return cursor.rowcount > 0
        except Exception as e:
            LOGGER.warning(f"Failed to create reference relationship: {e}")
            return False
    
    @staticmethod
    def get_by_type(type_id: int) -> List[Dict[str, Any]]:
        """Get all references for a type"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, t.name as to_name, t.kind as to_kind, f.path as to_file_path
                FROM references_table r
                JOIN types t ON r.to_id = t.id
                JOIN files f ON t.file_id = f.id
                WHERE r.from_id = ?
            """, (type_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete_by_type(type_id: int) -> int:
        """Delete all references for a type"""
        with DATABASE_CONNECTION.get_cursor() as cursor:
            cursor.execute("DELETE FROM references_table WHERE from_id = ? OR to_id = ?", (type_id, type_id))
            return cursor.rowcount
