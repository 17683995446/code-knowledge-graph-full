#!/usr/bin/env python3
"""Debug cache inconsistency issue"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.configuration import LOGGER
from src.database import DATABASE_CONNECTION, FileDAO, TypeDAO, FunctionDAO
from src.engine import IncrementalUpdateEngine
from src.parsers import initialize_all_parsers


def debug_cache_keys():
    """Debug why cache has inconsistency"""
    
    initialize_all_parsers()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple test file
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1

def func1():
    return 2
""")
        
        # Run engine
        engine = IncrementalUpdateEngine(Path(temp_dir))
        engine.initialize()
        stats = engine.full_sync()
        
        LOGGER.info("Initial sync done")
        
        # Let's debug!
        LOGGER.info("\n--- Cache keys ---")
        LOGGER.info(f"File cache: {len(engine._file_id_cache)}")
        LOGGER.info(f"Type cache: {len(engine._type_cache)}")
        for k in list(engine._type_cache.keys())[:5]:
            LOGGER.info(f"  Type key: {k}")
        
        LOGGER.info(f"\nFunc cache: {len(engine._function_cache)}")
        for k in list(engine._function_cache.keys())[:5]:
            LOGGER.info(f"  Func key: {k}")
        
        # Check DB
        LOGGER.info("\n--- From DB ---")
        db_stats = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"DB: {db_stats['total_files']} F, {db_stats['total_types']} T, {db_stats['total_functions']} Fn")
        
        functions_from_db = FunctionDAO.get_all()
        LOGGER.info(f"\n{len(functions_from_db)} functions from DB:")
        for f in functions_from_db[:5]:
            key = f"{f['name']}:{f['type_id']}:{f['file_id']}"
            LOGGER.info(f"  DB key: {key}")
            LOGGER.info(f"    name={f['name']}, type_id={f['type_id']}, file_id={f['file_id']}")
        
        # Now modify the file and see what happens!
        LOGGER.info("\n--- Modify and check ---")
        
        test_file.write_text("""
class TestClass:
    def method1(self):
        return 1
    def method2(self):
        return 2

def func1():
    return 2
def func2():
    return 3
""")
        
        update_stats = engine.process_events([test_file])
        LOGGER.info(f"Update: {update_stats}")
        
        LOGGER.info("\n--- Cache after update ---")
        LOGGER.info(f"Type cache: {len(engine._type_cache)}")
        for k in list(engine._type_cache.keys()):
            LOGGER.info(f"  Type key: {k}")
        
        LOGGER.info(f"\nFunc cache: {len(engine._function_cache)}")
        for k in list(engine._function_cache.keys()):
            LOGGER.info(f"  Func key: {k}")
        
        db_stats2 = DATABASE_CONNECTION.get_database_stats()
        LOGGER.info(f"\nDB now: {db_stats2['total_files']} F, {db_stats2['total_types']} T, {db_stats2['total_functions']} Fn")
        
        functions_from_db2 = FunctionDAO.get_all()
        LOGGER.info(f"\n{len(functions_from_db2)} functions from DB 2:")
        for f in functions_from_db2:
            key = f"{f['name']}:{f['type_id']}:{f['file_id']}"
            LOGGER.info(f"  DB key 2: {key}")
            LOGGER.info(f"    name={f['name']}, type_id={f['type_id']}, file_id={f['file_id']}")


if __name__ == "__main__":
    debug_cache_keys()
