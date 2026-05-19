"""
pytest configuration
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import tempfile

import pytest


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    import shutil
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def temp_db():
    """Create temporary database for tests"""
    import shutil
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp.close()
    yield Path(temp.name)
    try:
        os.unlink(temp.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file"""
    content = '''
class SampleClass:
    """A sample class"""
    
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value

def sample_function():
    """A sample function"""
    return 42
'''
    path = temp_dir / 'sample.py'
    path.write_text(content)
    return path
