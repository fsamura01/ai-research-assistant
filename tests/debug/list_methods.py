from qdrant_client import QdrantClient
client = QdrantClient(":memory:")
methods = sorted([m for m in dir(client) if not m.startswith('_')])
print("All available methods:")
for m in methods:
    print(f" - {m}")
