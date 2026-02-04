
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logfire
logfire.configure(send_to_logfire='never')

# Mock SentenceTransformer globally for this test file
with patch('sentence_transformers.SentenceTransformer'):
    from src.utils.vector_store import VectorStore
    from src.utils.document_loader import Document

@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end():
    # 1. Setup Vector Store with in-memory storage
    with patch('src.utils.vector_store.SentenceTransformer') as mock_st:
        mock_instance = MagicMock()
        mock_instance.encode.return_value.tolist.return_value = [[0.1]*768]
        mock_st.return_value = mock_instance
        
        print("\nSetting up Vector Store...")
        vector_store = VectorStore(collection_name="test_integration_rag", in_memory=True)
        vector_store.local_model = mock_instance
        
        # 2. Ingest a known document
        test_content = "The capital of France is Paris."
        doc = Document(content=test_content, metadata={"title": "Test Doc", "source_url": "test.com"})
        vector_store.add_documents([doc])
        
        # 3. Verify ingestion
        results = vector_store.search("France capital", top_k=1)
        assert len(results) > 0
        assert "Paris" in results[0]["text"]
        
        # 4. Test tool in isolation
        from src.tools.research_local_docs import research_local_docs
        
        # We don't need to patch VectorStore because research_local_docs 
        # uses the one provided in ctx.deps.
        mock_ctx = MagicMock()
        mock_ctx.deps = MagicMock()
        mock_ctx.deps.vector_store = vector_store
        
        tool_results = research_local_docs(mock_ctx, "What is the capital of France?")
        
        assert len(tool_results) > 0
        assert "Paris" in tool_results[0].snippet
        print(f"Tool Result snippet: {tool_results[0].snippet}")
