import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.research_agent import agent
from src.models.schemas import ResearchDeps
from src.utils.vector_store import VectorStore
from src.utils.document_loader import Document

async def test_iterative_loop():
    print("--- Phase 5: Iterative Loop Verification ---")
    vstore = VectorStore(collection_name="test_iterative_collection", in_memory=True)
    
    # Add distinct topics that need to be compared (Sanitized - no quotes)
    docs = [
        Document(
          content="Alice project uses a microservices architecture with 15 nodes and a central gateway.", 
          metadata={
            "source_type": "web", 
            "source_authority": 5, 
            "source_url": "http://alice.com"
            }
        ),
        Document(
          content="Bob project is a monolith deployed on a single high-performance server.", 
          metadata={
            "source_type": "web", 
            "source_authority": 5, 
            "source_url": "http://bob.com"
            }
        ),
        Document(
          content="Performance benchmarks show Alice setup handles 10k requests/sec.", 
          metadata={
            "source_type": "web", 
            "source_authority": 5, 
            "source_url": "http://benchmarks.com/alice"
            }
        ),
        Document(
          content="Bob server peaks at 5k requests/sec due to memory constraints.", 
          metadata={
            "source_type": "web", 
            "source_authority": 5, 
            "source_url": "http://benchmarks.com/bob"
            }
        )
    ]
    vstore.add_documents(docs)
    
    # Query requiring a deep dive (Architecture AND Performance for Alice vs Bob)
    query = "Contrast the architecture and performance of Alice project versus Bob project based on the documentation."
    print(f"\n[QUERY]: {query}")
    
    deps = ResearchDeps(api_key="mock", vector_store=vstore, min_authority=1)
    
    # Run the agent
    print("\n[AGENT STARTING REASONING...]")
    result = await agent.run(query, deps=deps)
    
    print("\n" + "="*50)
    print("FINAL AGENT RESPONSE")
    print("="*50)
    print(result.output)
    print("="*50)
    
if __name__ == "__main__":
    # Disable tqdm for cleaner logs
    import os
    os.environ["TQDM_DISABLE"] = "1"
    asyncio.run(test_iterative_loop())
