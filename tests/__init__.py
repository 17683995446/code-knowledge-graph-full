"""
Test suite configuration and utilities
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_test_suite():
    """Create the complete test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.discover('tests/unit', pattern='test_*.py'))
    suite.addTests(loader.discover('tests/integration', pattern='test_*.py'))
    suite.addTests(loader.discover('tests/system', pattern='test_*.py'))
    
    return suite


def run_tests():
    """Run all tests"""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
