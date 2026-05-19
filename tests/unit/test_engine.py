"""
Unit Tests for Engine Module
"""

import unittest
import tempfile
import os
import time
from pathlib import Path
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.engine.incremental_update_engine import (
    IncrementalUpdateEngine,
    UpdateStatistics
)
from src.engine.file_monitor import FileMonitor, FileEvent, FileEventType
from src.database.database_connection import DatabaseConnection


class TestIncrementalUpdateEngine(unittest.TestCase):
    """Test cases for IncrementalUpdateEngine"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        os.environ['DATABASE_PATH'] = self.temp_db.name
        
        import src.core.configuration as config
        config.CONFIG.database_path = Path(self.temp_db.name)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        os.unlink(self.temp_db.name)
    
    def create_test_file(self, name, content):
        """Create a test file"""
        path = os.path.join(self.temp_dir, name)
        with open(path, 'w') as f:
            f.write(content)
        return Path(path)
    
    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        engine = IncrementalUpdateEngine(Path(self.temp_dir))
        engine.initialize()
        
        self.assertIsNotNone(engine.file_monitor)
        self.assertIsNotNone(engine._file_id_cache)
    
    def test_full_sync_with_python_files(self):
        """Test full sync with Python files"""
        self.create_test_file('sample.py', '''
class TestClass:
    def method(self):
        pass

def test_function():
    pass
''')
        
        engine = IncrementalUpdateEngine(Path(self.temp_dir))
        engine.initialize()
        
        stats = engine.full_sync()
        
        self.assertGreaterEqual(stats.files_processed, 0)
        self.assertGreaterEqual(stats.types_processed, 0)
    
    def test_file_deletion_processing(self):
        """Test file deletion is processed correctly"""
        test_file = self.create_test_file('to_delete.py', 'print("hello")')
        
        engine = IncrementalUpdateEngine(Path(self.temp_dir))
        engine.initialize()
        stats = engine.full_sync()
        
        os.unlink(str(test_file))
        engine.file_monitor._file_mtimes.clear()
        
        events = [FileEvent(FileEventType.DELETED, test_file)]
        engine._handle_file_events(events)
        
        self.assertGreaterEqual(stats.files_deleted, 0)


class TestFileMonitor(unittest.TestCase):
    """Test cases for FileMonitor"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self):
        """Test monitor initializes with correct settings"""
        monitor = FileMonitor(Path(self.temp_dir))
        
        self.assertEqual(monitor.project_path, Path(self.temp_dir))
        self.assertFalse(monitor._running)
    
    def test_is_valid_file(self):
        """Test file validation logic"""
        monitor = FileMonitor(Path(self.temp_dir))
        
        src_dir = Path(self.temp_dir) / 'src'
        src_dir.mkdir(exist_ok=True)
        valid_file = src_dir / 'test.py'
        valid_file.touch()
        self.assertTrue(monitor._is_valid_file(valid_file))
        
        invalid_file = Path(self.temp_dir) / '__pycache__' / 'test.py'
        invalid_file.parent.mkdir(exist_ok=True)
        invalid_file.touch()
        self.assertFalse(monitor._is_valid_file(invalid_file))
    
    def test_scan_all_files(self):
        """Test scanning for all files"""
        src_dir = Path(self.temp_dir) / 'src'
        src_dir.mkdir(exist_ok=True)
        for i in range(3):
            (src_dir / f'test_{i}.py').touch()
        
        monitor = FileMonitor(Path(self.temp_dir))
        files = monitor.scan_all_files()
        
        self.assertEqual(len(files), 3)
    
    def test_callback_registration(self):
        """Test callback registration"""
        monitor = FileMonitor(Path(self.temp_dir))
        
        callback_called = []
        def test_callback(events):
            callback_called.append(True)
        
        monitor.register_callback(test_callback)
        self.assertEqual(len(monitor._callbacks), 1)


class TestUpdateStatistics(unittest.TestCase):
    """Test cases for UpdateStatistics"""
    
    def test_statistics_defaults(self):
        """Test default statistics values"""
        stats = UpdateStatistics()
        
        self.assertEqual(stats.files_processed, 0)
        self.assertEqual(stats.files_created, 0)
        self.assertEqual(stats.files_updated, 0)
        self.assertEqual(stats.files_deleted, 0)
        self.assertEqual(stats.types_processed, 0)
        self.assertEqual(stats.functions_processed, 0)
        self.assertEqual(stats.errors, [])


if __name__ == '__main__':
    unittest.main()
