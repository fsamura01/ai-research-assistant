
import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

try:
    from src.utils.vector_store import VectorStore
    from src.utils.document_loader import Document
    print("Imports successful")
    
    # Try to initialize
    # This might fail if it tries to load model or connect to Qdrant
    # But let's see where it fails
    store = VectorStore(in_memory=True)
    print("VectorStore initialized")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
