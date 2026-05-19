"""
Integration Tests for the Complete System
"""

import unittest
import tempfile
import os
import time
from pathlib import Path
import threading
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.configuration import CONFIG
from src.database.database_connection import DatabaseConnection
from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO
from src.parsers import initialize_all_parsers
from src.engine.incremental_update_engine import IncrementalUpdateEngine
from src.web_server import create_web_server


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test fixtures"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.temp_db.close()
        
        os.environ['DATABASE_PATH'] = cls.temp_db.name
        CONFIG.database_path = Path(cls.temp_db.name)
        CONFIG.project_path = Path(cls.temp_dir)
        
        initialize_all_parsers()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(cls.temp_dir)
        os.unlink(cls.temp_db.name)
    
    def create_test_file(self, name, content):
        """Create a test file"""
        path = os.path.join(self.temp_dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def test_complete_workflow(self):
        """Test complete system workflow"""
        self.create_test_file('models.py', '''
class User:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"

class Admin(User):
    def __init__(self, name, level):
        super().__init__(name)
        self.level = level
    
    def greet(self):
        return f"Hello Admin {self.name}"
''')
        
        self.create_test_file('utils.py', '''
def format_date(date):
    return date.strftime("%Y-%m-%d")

def calculate(a, b):
    return a + b
''')
        
        engine = IncrementalUpdateEngine(Path(self.temp_dir))
        engine.initialize()
        
        stats = engine.full_sync()
        
        self.assertGreaterEqual(stats.files_processed, 0)
        self.assertGreaterEqual(stats.types_processed, 0)
        self.assertGreaterEqual(stats.functions_processed, 0)
        
        file_count = len(FileDAO.get_all())
        self.assertEqual(file_count, 2)
        
        type_count = len(TypeDAO.get_all())
        self.assertGreater(type_count, 0)
    
    def test_incremental_update(self):
        """Test incremental update after file modification"""
        test_file = self.create_test_file('test.py', 'x = 1')
        
        engine = IncrementalUpdateEngine(Path(self.temp_dir))
        engine.initialize()
        engine.full_sync()
        
        db = DatabaseConnection(CONFIG.database_path)
        initial_stats = db.get_database_stats()
        
        time.sleep(0.1)
        with open(test_file, 'w') as f:
            f.write('y = 2\nz = 3')
        
        engine.file_monitor._file_mtimes[str(Path(test_file))] = Path(test_file).stat().st_mtime
        
        events = engine.file_monitor.scan_all_files()
        self.assertGreater(len(events), 0)
    
    def test_web_server_initialization(self):
        """Test web server initializes correctly"""
        web_server = create_web_server()
        self.assertIsNotNone(web_server)
        self.assertIsNotNone(web_server.app)
        self.assertIsNotNone(web_server.socketio)


class TestDatabaseIntegration(unittest.TestCase):
    """Database integration tests"""
    
    @classmethod
    def setUpClass(cls):
        """Setup database for testing"""
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.temp_db.close()
        
        os.environ['DATABASE_PATH'] = cls.temp_db.name
        CONFIG.database_path = Path(cls.temp_db.name)
        
        cls.db = DatabaseConnection(Path(cls.temp_db.name))
        cls.db.initialize_database()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup database"""
        os.unlink(cls.temp_db.name)
    
    def test_foreign_key_cascade(self):
        """Test foreign key cascading works"""
        from src.database.data_access_object import (
            FileDAO, TypeDAO, FunctionDAO,
            FileEntity, TypeEntity, FunctionEntity
        )
        
        file_entity = FileEntity(
            path='/test/cascade.py',
            language='python',
            hash=hashlib.md5(b'test').digest(),
            modified=1234567890
        )
        file_id = FileDAO.create(file_entity)
        
        type_entity = TypeEntity(
            name='TestClass',
            file_id=file_id,
            kind='class'
        )
        type_id = TypeDAO.create(type_entity)
        
        FileDAO.delete_by_id(file_id)
        
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM types WHERE id = ?", (type_id,))
            self.assertIsNone(cursor.fetchone())


class TestParserIntegration(unittest.TestCase):
    """Parser integration tests with different languages"""
    
    @classmethod
    def setUpClass(cls):
        """Setup parsers"""
        cls.temp_dir = tempfile.mkdtemp()
        initialize_all_parsers()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    def test_multi_language_parsing(self):
        """Test parsing files in multiple languages"""
        from src.parsers import get_parser_for_file
        
        files = {
            'test.py': ('class Test: pass', 'python'),
            'test.go': ('type Test struct {}', 'go'),
            'test.js': ('class Test {}', 'javascript'),
            'test.ts': ('interface Test {}', 'typescript')
        }
        
        for filename, (content, expected_lang) in files.items():
            path = Path(self.temp_dir) / filename
            path.write_text(content)
            
            parser = get_parser_for_file(path)
            if parser:
                result = parser.parse(path)
                self.assertIsNotNone(result)
                self.assertIn(result.language, [expected_lang, 'arkts'])


if __name__ == '__main__':
    unittest.main()
