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

async def test_strict_authority():
    print("--- Phase 3: Strict Authority Verification ---")
    vstore = VectorStore(collection_name="test_strict_collection", in_memory=True)
    
    # Add ONLY GitHub and Web docs
    docs = [
        Document(content="Task Manager Deployment: use websockets.", metadata={"source_type": "github", "source_authority": 9, "repo": "test/repo"}),
        Document(content="A neural network is a brain-like model.", metadata={"source_type": "web", "source_authority": 5, "source_url": "http://wiki.com"})
    ]
    vstore.add_documents(docs)
    
    # Test 1: High Authority (9) for Neural Networks (Should FAIL/Refuse)
    print("\n[TEST 1] Query: 'What is a neural network?' | Min Authority: 9")
    deps_high = ResearchDeps(api_key="mock", vector_store=vstore, min_authority=9)
    result_high = await agent.run("What is a neural network?", deps=deps_high)
    print(f"Agent Response:\n{result_high.output}")
    
    # Test 2: Low Authority (1) for Neural Networks (Should SUCCEED)
    print("\n[TEST 2] Query: 'What is a neural network?' | Min Authority: 1")
    deps_low = ResearchDeps(api_key="mock", vector_store=vstore, min_authority=1)
    result_low = await agent.run("What is a neural network?", deps=deps_low)
    print(f"Agent Response:\n{result_low.output}")

    # Test 3: High Authority (9) for Task Manager (Should SUCCEED using GitHub)
    print("\n[TEST 3] Query: 'How to deploy the task manager?' | Min Authority: 9")
    result_gh = await agent.run("How to deploy the task manager?", deps=deps_high)
    print(f"Agent Response:\n{result_gh.output}")

if __name__ == "__main__":
    asyncio.run(test_strict_authority())
