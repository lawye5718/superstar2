"""Global test configuration to ensure environment variables are set before any imports."""

import os

# Set environment variables BEFORE any app modules are imported
os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')
os.environ.setdefault('SQLALCHEMY_DATABASE_URL', 'sqlite:///./test.db')

# Force early import of the patched functions after environment is set
def pytest_configure():
    import sys
    # Clear any previously imported app modules to force re-import
    modules_to_remove = [k for k in sys.modules.keys() if k.startswith('app')]
    for module in modules_to_remove:
        del sys.modules[module]

    # Now import and cache the fixed functions
    from app.models.database import get_uuid_type
    print(f"UUID type configured as: {get_uuid_type()}")

