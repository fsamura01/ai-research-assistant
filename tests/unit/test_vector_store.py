
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logfire
logfire.configure(send_to_logfire='never')

from src.utils.vector_store import VectorStore
from src.utils.document_loader import Document

@pytest.fixture
def mock_qdrant_client():
    with patch('src.utils.vector_store.QdrantClient') as mock:
        yield mock

@pytest.fixture
def mock_groq_client():
    with patch('src.utils.vector_store.Groq') as mock:
        yield mock

@pytest.fixture
def vector_store(mock_qdrant_client, mock_groq_client):
    # Ensure Config uses local embedding for this test to avoid OpenAI calls
    with patch('src.utils.vector_store.Config') as MockConfig:
        MockConfig.EMBEDDING_PROVIDER = "local"
        MockConfig.CHUNK_SIZE = 100
        MockConfig.CHUNK_OVERLAP = 20
        MockConfig.COLLECTION_NAME = "test_collection"
        MockConfig.TOP_K_RESULTS = 3
        MockConfig.VECTOR_SIZE = 768
        
        with patch('src.utils.vector_store.SentenceTransformer') as mock_st:
            mock_instance = MagicMock()
            # Set up the mock instance to return a list when encoded
            # _get_embeddings returns a list of lists.
            # SentenceTransformer.encode returns a numpy array usually, calling .tolist() on it.
            mock_instance.encode.return_value.tolist.return_value = [[0.1]*768]
            mock_st.return_value = mock_instance
            
            vs = VectorStore(in_memory=True)
            vs.local_model = mock_instance
            return vs

def test_add_documents(vector_store):
    doc = Document(content="This is a test document.", metadata={"id": "doc1"})
    
    count = vector_store.add_documents([doc])
    
    assert count == 1
    # Check if upsert was called
    vector_store.qdrant_client.upsert.assert_called_once()

def test_search(vector_store):
    # Mock search return
    mock_point = MagicMock()
    mock_point.payload = {"text": "result text", "chunk_index": 0, "total_chunks": 1}
    mock_point.score = 0.95
    vector_store.qdrant_client.query_points.return_value.points = [mock_point]
    
    # Mock embedding for search query
    vector_store.local_model.encode.return_value.tolist.return_value = [[0.1]*768]
    
    results = vector_store.search("query")
    
    assert len(results) == 1
    assert results[0]["text"] == "result text"
    assert results[0]["score"] == 0.95
