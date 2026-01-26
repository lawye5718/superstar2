"""Run tests with proper environment setup"""

import os
import sys

# Set environment variables BEFORE importing any app modules
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///./test.db'

# Import and run tests
import pytest

if __name__ == "__main__":
    # Run specific test that was working
    exit_code = pytest.main(["-v", "tests/test_api.py::TestHealthEndpoints::test_root_endpoint"])
    sys.exit(exit_code)
