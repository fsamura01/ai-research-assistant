import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.vector_store import VectorStore
from src.utils.document_loader import Document

def test_authority_filter():
    print("Testing Source Authority Filter...")
    vstore = VectorStore(collection_name="test_filter_collection", in_memory=True)
    
    # Add docs with different authority
    docs = [
        Document(content="GitHub Content - High Trust", metadata={"source_type": "github", "source_authority": 9, "repo": "test/repo"}),
        Document(content="PDF Content - Med Trust", metadata={"source_type": "pdf", "source_authority": 7, "source_path": "test.pdf"}),
        Document(content="Web Content - Low Trust", metadata={"source_type": "web", "source_authority": 5, "source_url": "http://test.com"})
    ]
    
    vstore.add_documents(docs)
    
    print("\n1. Searching with min_authority=8 (Should only find GitHub)")
    res8 = vstore.search("Content", min_authority=8)
    for r in res8:
        print(f" - Found: {r['metadata']['source_type']} (Auth: {r['metadata']['source_authority']})")
    assert all(r['metadata']['source_authority'] >= 8 for r in res8)
    assert len(res8) > 0

    print("\n2. Searching with min_authority=6 (Should find GitHub and PDF)")
    res6 = vstore.search("Content", min_authority=6)
    for r in res6:
        print(f" - Found: {r['metadata']['source_type']} (Auth: {r['metadata']['source_authority']})")
    assert all(r['metadata']['source_authority'] >= 6 for r in res6)
    assert len(res6) > 0
    assert any(r['metadata']['source_type'] == "pdf" for r in res6)

    print("\n3. Searching with min_authority=1 (Should find all)")
    res1 = vstore.search("Content", min_authority=1)
    for r in res1:
        print(f" - Found: {r['metadata']['source_type']} (Auth: {r['metadata']['source_authority']})")
    assert len(res1) > 0
    assert any(r['metadata']['source_type'] == "web" for r in res1)

    print("\n[SUCCESS] Authority filtering works correctly!")

if __name__ == "__main__":
    try:
        test_authority_filter()
    except Exception as e:
        print(f"\n[FAILURE] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
