import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.vector_store import VectorStore
from src.utils.config import Config
import os

def test_embeddings():
    print("Testing embeddings...")
    try:
        vstore = VectorStore(in_memory=False)
        #print(vars(vstore))
        embedding = vstore._get_embedding("Verify embedding dimension")
        print(f"Success! Provider: {Config.EMBEDDING_PROVIDER}")
        print(f"Model: {Config.EMBEDDING_MODEL}")
        print(f"Embedding length: {len(embedding)}")
        assert len(embedding) == Config.VECTOR_SIZE, f"Expected {Config.VECTOR_SIZE}, got {len(embedding)}"
        print("Dimensions verified.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_embeddings()
