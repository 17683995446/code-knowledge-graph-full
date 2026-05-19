"""
Incremental Update Engine Module
Implements the core first principles: delete old + insert new
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..core.configuration import CONFIG, LOGGER
from ..database import (
    DATABASE_CONNECTION,
    FileDAO, TypeDAO, FunctionDAO, CallDAO, ReferenceDAO,
    FileEntity, TypeEntity, FunctionEntity,
    CallRelationship, ReferenceRelationship
)
from ..parsers import (
    UniversalParser, ParserRegistry,
    ParseResult, detect_language, get_parser_for_file
)
from .file_monitor import FileMonitor, FileEvent, FileEventType


@dataclass
class UpdateStatistics:
    """Statistics for update operations"""
    files_processed: int = 0
    files_created: int = 0
    files_updated: int = 0
    files_deleted: int = 0
    types_processed: int = 0
    functions_processed: int = 0
    calls_resolved: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class IncrementalUpdateEngine:
    """
    Incremental Update Engine following first principles:
    1. Each file is updated independently
    2. Update = Delete old data + Insert new data
    3. Only changed files are processed
    """
    
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or CONFIG.project_path
        self.file_monitor = FileMonitor(self.project_path)
        self.stats = UpdateStatistics()
        self._file_id_cache: Dict[str, int] = {}
        self._type_cache: Dict[str, Dict[str, Any]] = {}
        self._function_cache: Dict[str, Dict[str, Any]] = {}
        self._pending_calls: List[Dict[str, Any]] = []
    
    def initialize(self) -> None:
        """Initialize database and cache"""
        LOGGER.info("Initializing incremental update engine...")
        
        DATABASE_CONNECTION.initialize_database()
        
        self._load_cache()
        
        self.file_monitor.register_callback(self._handle_file_events)
        
        LOGGER.info(
            f"Engine initialized: {len(self._file_id_cache)} files, "
            f"{len(self._type_cache)} types, {len(self._function_cache)} functions cached"
        )
    
    def _load_cache(self) -> None:
        """Load existing data into memory cache"""
        files = FileDAO.get_all()
        self._file_id_cache = {f['path']: f['id'] for f in files}
        
        types = TypeDAO.get_all()
        self._type_cache = {
            f"{t['name']}:{t['file_id']}": t for t in types
        }
        
        functions = FunctionDAO.get_all()
        self._function_cache = {
            f"{f['name']}:{f['type_id']}:{f['file_id']}": f for f in functions
        }
    
    def full_sync(self) -> UpdateStatistics:
        """Perform full synchronization of all files"""
        LOGGER.info("Starting full sync...")
        start_time = time.time()
        
        self.stats = UpdateStatistics()
        self._pending_calls = []
        
        files = self.file_monitor.scan_all_files()
        LOGGER.info(f"Found {len(files)} files to process")
        
        all_parse_results: Dict[Path, ParseResult] = {}
        
        for file_path in files:
            try:
                parse_result = self._parse_file(file_path)
                if parse_result:
                    all_parse_results[file_path] = parse_result
                self.stats.files_processed += 1
            except Exception as e:
                LOGGER.error(f"Error parsing {file_path}: {e}")
                self.stats.errors.append(f"{file_path}: {e}")
        
        for file_path, parse_result in all_parse_results.items():
            try:
                self._process_and_store(file_path, parse_result)
            except Exception as e:
                LOGGER.error(f"Error processing {file_path}: {e}")
                self.stats.errors.append(f"{file_path}: {e}")
        
        self._resolve_all_pending_calls()
        
        elapsed = time.time() - start_time
        LOGGER.info(
            f"Full sync complete: {self.stats.files_processed} files in {elapsed:.2f}s, "
            f"{len(self.stats.errors)} errors"
        )
        LOGGER.info(
            f"  Types: {self.stats.types_processed}, "
            f"Functions: {self.stats.functions_processed}, "
            f"Calls resolved: {self.stats.calls_resolved}"
        )
        
        return self.stats
    
    def _parse_file(self, file_path: Path) -> Optional[ParseResult]:
        """Parse a file and return result"""
        path_str = str(file_path)
        language = detect_language(file_path)
        
        if not language:
            LOGGER.debug(f"Skipping unsupported file: {file_path}")
            return None
        
        parser = get_parser_for_file(file_path)
        if not parser:
            LOGGER.debug(f"No parser available for: {file_path}")
            return None
        
        parse_result = parser.parse(file_path)
        return parse_result
    
    def _process_and_store(self, file_path: Path, parse_result: ParseResult) -> None:
        """Process and store parsed result"""
        path_str = str(file_path)
        language = detect_language(file_path)
        
        existing_file_id = self._file_id_cache.get(path_str)
        
        if existing_file_id:
            # 清理旧的缓存数据（修复Bug：删除文件相关的类型和函数缓存）
            keys_to_remove = [k for k in self._type_cache if self._type_cache[k]['file_id'] == existing_file_id]
            for key in keys_to_remove:
                del self._type_cache[key]
            
            keys_to_remove = [k for k in self._function_cache if self._function_cache[k]['file_id'] == existing_file_id]
            for key in keys_to_remove:
                del self._function_cache[key]
            
            FileDAO.delete_by_id(existing_file_id)
            LOGGER.debug(f"Updated file: {file_path}")
            self.stats.files_updated += 1
        else:
            self.stats.files_created += 1
        
        file_entity = FileEntity(
            path=path_str,
            language=language,
            hash=parse_result.file_hash,
            modified=parse_result.modified_time
        )
        file_id = FileDAO.create(file_entity)
        self._file_id_cache[path_str] = file_id
        
        type_name_to_id: Dict[str, int] = {}
        local_function_ids: Dict[str, int] = {}
        
        for type_info in parse_result.types:
            type_entity = TypeEntity(
                name=type_info['name'],
                file_id=file_id,
                kind=type_info['kind'],
                flags=type_info.get('flags', 0),
                start_line=type_info.get('start_line'),
                end_line=type_info.get('end_line'),
                docstring=type_info.get('docstring')
            )
            type_id = TypeDAO.create(type_entity)
            type_name_to_id[type_info['name']] = type_id
            
            cache_key = f"{type_info['name']}:{file_id}"
            self._type_cache[cache_key] = {'id': type_id, **type_info, 'file_id': file_id}
            
            self.stats.types_processed += 1
            
            for base in type_info.get('base_classes', []):
                base_cache_key = f"{base}:{file_id}"
                if base_cache_key in self._type_cache:
                    ref = ReferenceRelationship(
                        from_id=type_id,
                        to_id=self._type_cache[base_cache_key]['id'],
                        kind='extends'
                    )
                    ReferenceDAO.create(ref)
        
        for func_info in parse_result.functions:
            type_id = type_name_to_id.get(func_info.get('type_name'))
            
            func_entity = FunctionEntity(
                name=func_info['name'],
                type_id=type_id,
                file_id=file_id,
                start_line=func_info.get('start_line'),
                end_line=func_info.get('end_line'),
                signature=func_info.get('signature'),
                docstring=func_info.get('docstring')
            )
            func_id = FunctionDAO.create(func_entity)
            
            func_cache_key = f"{func_info['name']}:{type_id}:{file_id}"
            self._function_cache[func_cache_key] = {
                'id': func_id,
                'name': func_info['name'],
                'type_id': type_id,
                'file_id': file_id,
                **func_info
            }
            
            local_function_ids[func_info['name']] = func_id
            self.stats.functions_processed += 1
            
            for callee_name in func_info.get('calls', []):
                self._pending_calls.append({
                    'caller_id': func_id,
                    'caller_name': func_info['name'],
                    'callee_name': callee_name,
                    'file_id': file_id
                })
        
        for imp_info in parse_result.imports:
            with DATABASE_CONNECTION.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO import_statements (file_id, module_path, imported_names, is_wildcard)
                    VALUES (?, ?, ?, ?)
                """, (
                    file_id,
                    imp_info['module_path'],
                    ','.join(imp_info.get('imported_names', [])),
                    1 if imp_info.get('is_wildcard') else 0
                ))
    
    def _resolve_all_pending_calls(self) -> None:
        """Resolve all pending call relationships"""
        LOGGER.debug(f"Resolving {len(self._pending_calls)} pending calls")
        
        for call_info in self._pending_calls:
            caller_id = call_info['caller_id']
            callee_name = call_info['callee_name']
            file_id = call_info['file_id']
            
            for func_key, func_data in self._function_cache.items():
                if func_data['name'] == callee_name:
                    call_rel = CallRelationship(
                        caller_id=caller_id,
                        callee_id=func_data['id']
                    )
                    if CallDAO.create(call_rel):
                        self.stats.calls_resolved += 1
                    break
        
        self._pending_calls = []
    
    def start_monitoring(self) -> None:
        """Start file monitoring for incremental updates"""
        LOGGER.info("Starting file monitoring...")
        self.file_monitor.start()
        self._running = True
    
    def stop_monitoring(self) -> None:
        """Stop file monitoring"""
        LOGGER.info("Stopping file monitoring...")
        self._running = False
        if self.file_monitor:
            self.file_monitor.stop()
        LOGGER.info("File monitoring stopped")
    
    def _handle_file_events(self, events: List[FileEvent]) -> None:
        """Handle batch of file events"""
        for event in events:
            try:
                if event.event_type == FileEventType.DELETED:
                    self._process_file_deletion(event.file_path)
                else:
                    self._process_single_file_update(event.file_path)
            except Exception as e:
                LOGGER.error(f"Error handling event for {event.file_path}: {e}")
                self.stats.errors.append(f"{event.file_path}: {e}")
    
    def _process_file_deletion(self, file_path: Path) -> None:
        """Process file deletion: remove all related data"""
        path_str = str(file_path)
        
        if path_str not in self._file_id_cache:
            return
        
        file_id = self._file_id_cache[path_str]
        
        FileDAO.delete_by_id(file_id)
        
        keys_to_remove = [k for k in self._type_cache if self._type_cache[k]['file_id'] == file_id]
        for key in keys_to_remove:
            del self._type_cache[key]
        
        keys_to_remove = [k for k in self._function_cache if self._function_cache[k]['file_id'] == file_id]
        for key in keys_to_remove:
            del self._function_cache[key]
        
        del self._file_id_cache[path_str]
        
        LOGGER.debug(f"Deleted file: {file_path}")
        self.stats.files_deleted += 1
    
    def process_events(self, file_paths: List[Path]) -> UpdateStatistics:
        """Process file events and perform incremental updates
        
        Args:
            file_paths: List of file paths that have changed
            
        Returns:
            UpdateStatistics with results of the update
        """
        old_stats = UpdateStatistics(
            files_processed=self.stats.files_processed,
            files_created=self.stats.files_created,
            files_updated=self.stats.files_updated,
            files_deleted=self.stats.files_deleted,
            types_processed=self.stats.types_processed,
            functions_processed=self.stats.functions_processed,
            calls_resolved=self.stats.calls_resolved
        )
        
        for file_path in file_paths:
            if file_path.exists():
                self._process_single_file_update(file_path)
            else:
                self._process_file_deletion(file_path)
        
        # Return the incremental changes
        return UpdateStatistics(
            files_processed=self.stats.files_processed - old_stats.files_processed,
            files_created=self.stats.files_created - old_stats.files_created,
            files_updated=self.stats.files_updated - old_stats.files_updated,
            files_deleted=self.stats.files_deleted - old_stats.files_deleted,
            types_processed=self.stats.types_processed - old_stats.types_processed,
            functions_processed=self.stats.functions_processed - old_stats.functions_processed,
            calls_resolved=self.stats.calls_resolved - old_stats.calls_resolved
        )
    
    def _process_single_file_update(self, file_path: Path) -> None:
        """Process single file update"""
        self._pending_calls = []
        
        parse_result = self._parse_file(file_path)
        if not parse_result:
            return
        
        self._process_and_store(file_path, parse_result)
        self._resolve_all_pending_calls()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        db_stats = DATABASE_CONNECTION.get_database_stats()
        
        return {
            'cache': {
                'files': len(self._file_id_cache),
                'types': len(self._type_cache),
                'functions': len(self._function_cache)
            },
            'updates': {
                'files_processed': self.stats.files_processed,
                'files_created': self.stats.files_created,
                'files_updated': self.stats.files_updated,
                'files_deleted': self.stats.files_deleted,
                'types_processed': self.stats.types_processed,
                'functions_processed': self.stats.functions_processed,
                'calls_resolved': self.stats.calls_resolved
            },
            'database': db_stats
        }


def create_update_engine(project_path: Optional[Path] = None) -> IncrementalUpdateEngine:
    """Factory function to create update engine"""
    return IncrementalUpdateEngine(project_path)
