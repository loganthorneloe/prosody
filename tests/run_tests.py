#!/usr/bin/env python3
"""
Comprehensive test runner for Prosody dictation tool
"""

import unittest
import sys
import argparse
import time
from pathlib import Path
from io import StringIO

# Add parent directory to Python path to find prosody module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all test modules
from test_prosody import *
from test_platform_specific import *


class TestResult:
    """Custom test result tracker"""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = 0
        self.errors = 0
        self.skipped = 0
        self.start_time = None
        self.end_time = None
        self.failure_details = []
        self.error_details = []
    
    def start_timer(self):
        self.start_time = time.time()
    
    def stop_timer(self):
        self.end_time = time.time()
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    @property
    def success_rate(self):
        if self.tests_run == 0:
            return 0
        return ((self.tests_run - self.failures - self.errors) / self.tests_run) * 100


def run_test_suite(test_classes, verbosity=2, failfast=False):
    """Run a specific set of test classes"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load tests from specified classes
    for test_class in test_classes:
        if isinstance(test_class, str):
            # Load by name
            tests = loader.loadTestsFromName(test_class)
        else:
            # Load by class
            tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    result = TestResult()
    result.start_timer()
    
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        stream=sys.stdout
    )
    unittest_result = runner.run(suite)
    
    result.stop_timer()
    result.tests_run = unittest_result.testsRun
    result.failures = len(unittest_result.failures)
    result.errors = len(unittest_result.errors)
    result.skipped = len(unittest_result.skipped)
    result.failure_details = unittest_result.failures
    result.error_details = unittest_result.errors
    
    return result


def run_quick_tests():
    """Run a quick subset of tests for fast feedback"""
    quick_tests = [
        TestConfig,
        TestDictationState,
        'test_prosody.TestDeviceManager.test_get_best_device_mps',
        'test_prosody.TestTextRefinementService.test_basic_text_cleanup',
    ]
    
    print("🚀 Running quick tests...")
    result = run_test_suite(quick_tests, verbosity=1)
    print_summary(result, "Quick Tests")
    return result


def run_unit_tests():
    """Run all unit tests"""
    unit_tests = [
        TestConfig,
        TestDictationState,
        TestConsoleUI,
        TestDeviceManager,
        TestTranscriptionService,
        TestTextRefinementService,
        TestTypingService,
        TestHotkeyListener,
        TestAudioRecorder,
        TestPermissionManager,
    ]
    
    print("🧪 Running unit tests...")
    result = run_test_suite(unit_tests, verbosity=2)
    print_summary(result, "Unit Tests")
    return result


def run_integration_tests():
    """Run integration tests"""
    integration_tests = [
        TestAppController,
        TestCreateApp,
    ]
    
    print("🔗 Running integration tests...")
    result = run_test_suite(integration_tests, verbosity=2)
    print_summary(result, "Integration Tests")
    return result


def run_platform_tests():
    """Run platform-specific tests"""
    platform_tests = [
        TestCrossPlatformDeviceDetection,
        TestPlatformSpecificBehavior,
        TestConfigurationVariations,
    ]
    
    print("🖥️  Running platform tests...")
    result = run_test_suite(platform_tests, verbosity=2)
    print_summary(result, "Platform Tests")
    return result


def run_error_handling_tests():
    """Run error handling tests"""
    error_tests = [
        TestErrorHandling,
    ]
    
    print("⚠️  Running error handling tests...")
    result = run_test_suite(error_tests, verbosity=2)
    print_summary(result, "Error Handling Tests")
    return result


def run_all_tests():
    """Run complete test suite"""
    all_tests = [
        TestConfig,
        TestDictationState,
        TestConsoleUI,
        TestDeviceManager,
        TestTranscriptionService,
        TestTextRefinementService,
        TestTypingService,
        TestHotkeyListener,
        TestAudioRecorder,
        TestPermissionManager,
        TestAppController,
        TestCreateApp,
        TestErrorHandling,
        TestCrossPlatformDeviceDetection,
        TestPlatformSpecificBehavior,
        TestConfigurationVariations,
    ]
    
    print("🎯 Running complete test suite...")
    result = run_test_suite(all_tests, verbosity=2)
    print_summary(result, "Complete Test Suite")
    return result


def print_summary(result, test_name):
    """Print a formatted test summary"""
    print(f"\n{'='*60}")
    print(f"{test_name} Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.tests_run}")
    print(f"Failures: {result.failures}")
    print(f"Errors: {result.errors}")
    print(f"Skipped: {result.skipped}")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(f"Duration: {result.duration:.2f}s")
    
    if result.failures > 0:
        print(f"\n❌ {result.failures} test(s) failed:")
        for test, traceback in result.failure_details:
            print(f"  - {test}")
    
    if result.errors > 0:
        print(f"\n💥 {result.errors} test(s) had errors:")
        for test, traceback in result.error_details:
            print(f"  - {test}")
    
    if result.failures == 0 and result.errors == 0:
        print("✅ All tests passed!")
    
    print(f"{'='*60}\n")


def run_coverage_report():
    """Generate coverage report if coverage is available"""
    try:
        import coverage
        
        print("📊 Generating coverage report...")
        
        # Start coverage
        cov = coverage.Coverage(source=['prosody'])
        cov.start()
        
        # Run all tests
        result = run_all_tests()
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        print("-" * 60)
        cov.report(show_missing=True)
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print(f"\nHTML coverage report: file://{Path.cwd()}/htmlcov/index.html")
        
        return result
        
    except ImportError:
        print("❌ Coverage module not installed. Install with: pip install coverage")
        return run_all_tests()


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description='Prosody Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Suites:
  quick       - Fast subset of tests for quick feedback
  unit        - All unit tests
  integration - Integration tests
  platform    - Platform-specific tests  
  errors      - Error handling tests
  all         - Complete test suite (default)
  coverage    - All tests with coverage report

Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py quick              # Quick tests
  python run_tests.py unit --verbose     # Unit tests with high verbosity
  python run_tests.py coverage           # Generate coverage report
        """
    )
    
    parser.add_argument(
        'suite',
        nargs='?',
        default='all',
        choices=['quick', 'unit', 'integration', 'platform', 'errors', 'all', 'coverage'],
        help='Test suite to run (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Increase test verbosity'
    )
    
    parser.add_argument(
        '-f', '--failfast',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List all available tests'
    )
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("Available test classes:")
        test_classes = [
            TestConfig,
            TestDictationState,
            TestConsoleUI,
            TestDeviceManager,
            TestTranscriptionService,
            TestTextRefinementService,
            TestTypingService,
            TestHotkeyListener,
            TestAudioRecorder,
            TestPermissionManager,
            TestAppController,
            TestCreateApp,
            TestErrorHandling,
            TestCrossPlatformDeviceDetection,
            TestPlatformSpecificBehavior,
            TestConfigurationVariations,
        ]
        for test_class in test_classes:
            print(f"  - {test_class.__name__}")
        return 0
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Run selected test suite
    suite_runners = {
        'quick': run_quick_tests,
        'unit': run_unit_tests,
        'integration': run_integration_tests,
        'platform': run_platform_tests,
        'errors': run_error_handling_tests,
        'all': run_all_tests,
        'coverage': run_coverage_report,
    }
    
    start_time = time.time()
    result = suite_runners[args.suite]()
    total_time = time.time() - start_time
    
    print(f"🏁 Total execution time: {total_time:.2f}s")
    
    # Return appropriate exit code
    if result.failures > 0 or result.errors > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())