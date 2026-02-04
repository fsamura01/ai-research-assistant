
import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

if __name__ == "__main__":
    retcode = pytest.main(["-v", "tests/unit/test_vector_store.py"])
    sys.exit(retcode)
