"""
System Tests for End-to-End Scenarios
"""

import unittest
import tempfile
import os
import time
import subprocess
import threading
from pathlib import Path
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestEndToEndScenarios(unittest.TestCase):
    """End-to-end system tests"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.temp_db.close()
        
        os.environ['DATABASE_PATH'] = cls.temp_db.name
        os.environ['PROJECT_PATH'] = cls.temp_dir
        os.environ['LOG_LEVEL'] = 'INFO'
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        import shutil
        shutil.rmtree(cls.temp_dir)
        os.unlink(cls.temp_db.name)
    
    def create_sample_project(self):
        """Create a sample project structure"""
        project_structure = {
            'src': {
                '__init__.py': '',
                'main.py': '''
from pathlib import Path

class Application:
    def __init__(self):
        self.name = "TestApp"
    
    def run(self):
        print("Running...")

def main():
    app = Application()
    app.run()
''',
                'utils': {
                    '__init__.py': '',
                    'helpers.py': '''
import os

def get_env(key, default=None):
    return os.environ.get(key, default)

def validate_path(path):
    return Path(path).exists()
'''
                }
            },
            'tests': {
                '__init__.py': '',
                'test_main.py': '''
import unittest
from src.main import Application

class TestApp(unittest.TestCase):
    def test_initialization(self):
        app = Application()
        self.assertEqual(app.name, "TestApp")
'''
            }
        }
        
        def create_structure(base, structure):
            for name, content in structure.items():
                path = Path(base) / name
                if isinstance(content, dict):
                    path.mkdir(exist_ok=True)
                    create_structure(path, content)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
        
        create_structure(self.temp_dir, project_structure)
    
    def test_project_parsing(self):
        """Test parsing a complete project"""
        self.create_sample_project()
        
        from src.core.configuration import CONFIG
        CONFIG.database_path = Path(self.temp_db.name)
        CONFIG.project_path = Path(self.temp_dir)
        
        from src.database.database_connection import DatabaseConnection
        from src.parsers import initialize_all_parsers
        from src.engine.incremental_update_engine import IncrementalUpdateEngine
        
        db = DatabaseConnection(CONFIG.database_path)
        db.initialize_database()
        
        initialize_all_parsers()
        
        engine = IncrementalUpdateEngine(CONFIG.project_path)
        engine.initialize()
        
        stats = engine.full_sync()
        
        self.assertGreater(stats.files_processed, 0)
        self.assertGreater(stats.types_processed, 0)
        self.assertGreater(stats.functions_processed, 0)
    
    def test_file_modification_detection(self):
        """Test detection of file modifications"""
        self.create_sample_project()
        
        from src.core.configuration import CONFIG
        CONFIG.database_path = Path(self.temp_db.name)
        CONFIG.project_path = Path(self.temp_dir)
        
        from src.database.database_connection import DatabaseConnection
        from src.parsers import initialize_all_parsers
        from src.engine.incremental_update_engine import IncrementalUpdateEngine
        
        db = DatabaseConnection(CONFIG.database_path)
        db.initialize_database()
        
        initialize_all_parsers()
        
        engine = IncrementalUpdateEngine(CONFIG.project_path)
        engine.initialize()
        engine.full_sync()
        
        main_file = Path(self.temp_dir) / 'src' / 'main.py'
        original_content = main_file.read_text()
        
        modified_content = original_content + '\n# Modified'
        main_file.write_text(modified_content)
        
        engine.file_monitor._file_mtimes.clear()
        engine.file_monitor._scan_initial_state()
        
        events = engine.file_monitor.scan_all_files()
        self.assertGreater(len(events), 0)
    
    def test_database_query_performance(self):
        """Test database query performance"""
        self.create_sample_project()
        
        from src.core.configuration import CONFIG
        CONFIG.database_path = Path(self.temp_db.name)
        CONFIG.project_path = Path(self.temp_dir)
        
        from src.database.database_connection import DatabaseConnection
        from src.parsers import initialize_all_parsers
        from src.engine.incremental_update_engine import IncrementalUpdateEngine
        
        db = DatabaseConnection(CONFIG.database_path)
        db.initialize_database()
        
        initialize_all_parsers()
        
        engine = IncrementalUpdateEngine(CONFIG.project_path)
        engine.initialize()
        engine.full_sync()
        
        start_time = time.time()
        
        from src.database.data_access_object import FileDAO, TypeDAO, FunctionDAO
        
        files = FileDAO.get_all()
        types = TypeDAO.get_all()
        functions = FunctionDAO.get_all()
        
        query_time = time.time() - start_time
        
        self.assertLess(query_time, 1.0)


class TestCLIInterface(unittest.TestCase):
    """Test CLI interface"""
    
    def test_main_module_imports(self):
        """Test main module can be imported"""
        import src.main
        self.assertIsNotNone(src.main)
    
    def test_configuration_loading(self):
        """Test configuration loads correctly"""
        from src.core.configuration import CONFIG
        
        self.assertIsNotNone(CONFIG)
        self.assertIsNotNone(CONFIG.project_path)


if __name__ == '__main__':
    unittest.main()
