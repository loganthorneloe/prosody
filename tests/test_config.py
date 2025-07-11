#!/usr/bin/env python3
"""
Test configuration and utilities for Prosody test suite
"""

import unittest
import sys
from pathlib import Path

# Test suite configurations
TEST_SUITES = {
    'unit': [
        'test_prosody.TestConfig',
        'test_prosody.TestDictationState',
        'test_prosody.TestConsoleUI',
        'test_prosody.TestDeviceManager',
        'test_prosody.TestTranscriptionService',
        'test_prosody.TestTextRefinementService',
        'test_prosody.TestTypingService',
        'test_prosody.TestHotkeyListener',
        'test_prosody.TestAudioRecorder',
        'test_prosody.TestPermissionManager',
    ],
    'integration': [
        'test_prosody.TestAppController',
        'test_prosody.TestCreateApp',
    ],
    'error_handling': [
        'test_prosody.TestErrorHandling',
    ],
    'all': [
        'test_prosody.TestConfig',
        'test_prosody.TestDictationState',
        'test_prosody.TestConsoleUI',
        'test_prosody.TestDeviceManager',
        'test_prosody.TestTranscriptionService',
        'test_prosody.TestTextRefinementService',
        'test_prosody.TestTypingService',
        'test_prosody.TestHotkeyListener',
        'test_prosody.TestAudioRecorder',
        'test_prosody.TestPermissionManager',
        'test_prosody.TestAppController',
        'test_prosody.TestCreateApp',
        'test_prosody.TestErrorHandling',
    ]
}


def run_test_suite(suite_name='all', verbosity=2):
    """Run a specific test suite"""
    if suite_name not in TEST_SUITES:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {list(TEST_SUITES.keys())}")
        return False
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in TEST_SUITES[suite_name]:
        try:
            tests = loader.loadTestsFromName(test_class)
            suite.addTests(tests)
        except Exception as e:
            print(f"Failed to load test class {test_class}: {e}")
            return False
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def generate_test_report():
    """Generate a test coverage report"""
    try:
        import coverage
        
        # Start coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run all tests
        success = run_test_suite('all', verbosity=1)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        cov.report(show_missing=True)
        
        # Generate HTML report
        cov.html_report(directory='coverage_html')
        print("HTML coverage report generated in 'coverage_html' directory")
        
        return success
        
    except ImportError:
        print("Coverage module not installed. Install with: pip install coverage")
        return run_test_suite('all')


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Prosody test suites')
    parser.add_argument('suite', nargs='?', default='all', 
                       choices=list(TEST_SUITES.keys()),
                       help='Test suite to run')
    parser.add_argument('-v', '--verbosity', type=int, default=2,
                       help='Test verbosity level')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    
    args = parser.parse_args()
    
    if args.coverage:
        success = generate_test_report()
    else:
        success = run_test_suite(args.suite, args.verbosity)
    
    sys.exit(0 if success else 1)