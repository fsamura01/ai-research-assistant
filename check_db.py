from qdrant_client import QdrantClient
import os

def check_db():
    db_paths = ["qdrant_data", "projects/week1_learning_assistant/qdrant_data"]
    
    for db_path in db_paths:
        print(f"\n--- Checking {db_path} ---")
        if not os.path.exists(db_path):
            print(f"ERROR: Database path {db_path} does not exist!")
            continue
        
        try:
            client = QdrantClient(path=db_path)
            collections = client.get_collections().collections
            print(f"Found {len(collections)} collections: {[c.name for c in collections]}")
            
            for c in collections:
                count = client.count(collection_name=c.name).count
                print(f"Collection '{c.name}' has {count} points.")
        except Exception as e:
            print(f"ERROR checking {db_path}: {e}")

if __name__ == "__main__":
    check_db()
