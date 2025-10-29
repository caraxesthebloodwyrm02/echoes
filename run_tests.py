#!/usr/bin/env python3
"""
Test runner for Echoes Assistant V2

Run all tests:
    python run_tests.py

Run specific test class:
    python run_tests.py TestModelRouter

Run specific test method:
    python run_tests.py TestModelRouter.test_simple_prompt_selection
"""
import unittest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def run_tests(test_name=None, verbosity=2):
    """Run the tests"""
    # Discover all test files
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test files
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if os.path.exists(test_dir):
        tests = test_loader.discover(test_dir, pattern='test_*.py')
        test_suite.addTest(tests)
    
    # If a specific test was specified, run only that
    if test_name:
        test_suite = test_loader.loadTestsFromName(test_name)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(test_suite)
    
    # Return success/failure
    return result.wasSuccessful()

if __name__ == '__main__':
    # Parse command line arguments
    test_name = None
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
    
    # Run the tests
    success = run_tests(test_name)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
