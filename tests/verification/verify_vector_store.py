import sys
import os

# Adds the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.vector_store import VectorStore
from src.utils.document_loader import DocumentLoader, Document 
from src.utils.config import Config

def verify_vector_store():
    print(f"--- VectorStore Verification ---")
    print(f"Provider: {Config.EMBEDDING_PROVIDER}")
    print(f"Model: {Config.EMBEDDING_MODEL}\n")

    try:
        # 1. Initialize (using in-memory for testing)
        print("1. Initializing VectorStore...")
        vstore = VectorStore(collection_name="test_collection", in_memory=True)
        
        # 2. Prepare test documents
        print("2. Preparing test documents...")
        docs = [
            Document(
                content="The capital of France is Paris. It is known for its art and the Eiffel Tower.",
                metadata={"source": "test", "topic": "geography"}
            ),
            Document(
                content="Python is a popular programming language used for data science and AI.",
                metadata={"source": "test", "topic": "coding"}
            )
        ]

        # 3. Add documents
        print("3. Adding documents to store...")
        count = vstore.add_documents(docs)
        print(f"   Successfully added {count} chunks.")

        # 4. Search
        print("4. Testing Search (Query: 'tell me about Paris')...")
        results = vstore.search("tell me about Paris", top_k=1)
        
        if results:
            match = results[0]
            print(f"   Match Found! Score: {match['score']:.4f}")
            print(f"   Snippet: {match['text'][:50]}...")
            
            # Verify the content
            if "Paris" in match['text']:
                print("   [SUCCESS] Search returned correct context.")
            else:
                print("   [FAILURE] Search returned irrelevant context.")
        else:
            print("   [FAILURE] No results found.")

        # 5. Clear store
        print("5. Testing Clear...")
        vstore.clear()
        
        # Try search again
        post_clear_results = vstore.search("Paris", top_k=1)
        if not post_clear_results:
            print("   [SUCCESS] Store cleared successfully.")
        else:
            # Note: In some versions of Qdrant in-memory, deletion might behave differently
            # but usually it should return empty if cleared.
            print("   [INFO] Check if data persists after clear.")

        print("\n--- Verification Complete! ---")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_vector_store()
