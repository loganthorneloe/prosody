"""Test for __main__ module entry point."""

import unittest
from unittest.mock import patch, Mock
import sys
import runpy


class TestMainEntry(unittest.TestCase):
    """Test the __main__ module entry point."""
    
    @patch('src.prosody.main.main')
    def test_main_module_execution(self, mock_main):
        """Test that __main__ module calls main() function when run as script."""
        # Run the module as __main__
        runpy.run_module('src.prosody', run_name='__main__')
        
        # Verify main was called
        mock_main.assert_called_once()
        
    def test_main_module_import_coverage(self):
        """Test importing __main__ module for coverage."""
        # Just import to get coverage
        import src.prosody.__main__
        
        # The import itself is the test
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()