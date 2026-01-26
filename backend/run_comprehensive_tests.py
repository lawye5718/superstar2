"""Run comprehensive tests with proper environment setup"""

import os
import sys

# Set environment variables BEFORE importing any app modules
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///./test.db'

# Import and run tests
import pytest

if __name__ == "__main__":
    # Run a broader set of tests
    args = [
        "-v", 
        "tests/test_api.py::TestHealthEndpoints",
        "tests/test_api.py::TestUserEndpoints::test_create_user_success",
        "tests/test_api.py::TestAuthEndpoints::test_login_success"
    ]
    exit_code = pytest.main(args)
    sys.exit(exit_code)
