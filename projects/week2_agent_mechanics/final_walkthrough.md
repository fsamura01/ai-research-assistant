# Week 2 Final Walkthrough: Agent Mechanics & Real Tool Integration

We have successfully built a production-ready Agentic Research Assistant.

## What We Built
We moved from a manual "Thought/Action/Observation" loop to a sophisticated agent powered by PydanticAI.

### 1. The Core Brain
Our agent now uses llama-3.3-70b (via Groq) to orchestrate complex research tasks. It follows strict system prompts to decide which tool to use.

### 2. The Integrated "Hands" (Real Tools)
The agent is no longer mocking its abilities. It is connected to:

Real Vector Search: Queries the Qdrant database we built in Week 1 to find your local documents.
Real Web Search: Uses the Tavily API to find current news and "live" information from the internet.
YouTube Transcripts: Uses youtube-transcript-api to "read" video content provided via URL.
Persistence: A 
save_note
 tool that writes findings into local Markdown files in the research_notes/ directory.
### 3. Safety & Robustness
Type Validation: Every tool argument is validated by Pydantic. If the LLM tries to send a string when we expect a number, it's caught and corrected.
Dependency Injection: API keys and database clients are passed safely through RunContext.
### 4. Verification
Verified: The agent can successfully search the web, summarize findings, and save them to a file.
Tests: 
test_pydantic_agent.py
 provides a suite for mocking and verifying agentic flows without spending API credits.
### 5. How to Run
Ensure your 
.env
 has GROQ_API_KEY and TAVILY_API_KEY.
Run the assistant:
uv run projects/week2_agent_mechanics/advanced_pydantic_ai.py
Check the research_notes/ folder for your saved research!
Week 2 Complete! We are now ready for Week 3: Evaluation and Monitoring.

## Week 3 Walkthrough: Evaluation, Benchmarking, and Monitoring
I have successfully implemented the monitoring and evaluation suite for the AI Research Assistant.

### 1. Monitoring with Logfire
Integrated Logfire for observability. Key methods in 
VectorStore
 and ResearchAgent are now instrumented to provide traces of the RAG pipeline.

Changes:
Added logfire dependency to 
pyproject.toml
.
Configured Logfire in 
src/utils/vector_store.py
 and 
src/agents/research_agent.py
.
Instrumented 
add_documents
 and 
search
 methods.
### 2. Automated Testing
Implemented unit and integration tests to ensure system reliability.

Verified:
Unit Tests: 
tests/unit/test_vector_store.py
 verifies document ingestion and search using mocked Qdrant and SentenceTransformers.
Integration Tests: 
tests/integration/test_rag_pipeline.py
 verifies the end-to-end flow from tool call to retrieval.
# Run unit tests
uv run pytest tests/unit/test_vector_store.py
# Run integration tests
uv run pytest tests/integration/test_rag_pipeline.py
3. Evaluation Data Generation
Created a synthetic data generator to create ground truth for benchmarking.

Script: 
src/evaluation/data_generator.py
Output: 
data/eval/testset.jsonl
 (Question-Answer pairs generated from 
docker_cheatsheet.pdf
).
### 4. LLM Judges & Benchmarking
Implemented an LLM-based evaluation system to score the RAG agent on Correctness and Faithfulness.

Judge: 
src/evaluation/judges.py
 (Scores 1-5 with reasoning).
Benchmark Run: 
src/evaluation/run_benchmark.py
Benchmark Results:
Metric	Average Score
Correctness	5.00 / 5
Faithfulness	3.50 / 5
NOTE

The faithfulness score (3.5/5) indicates that the agent occasionally adds helpful but external information (e.g., security benefits of Docker) that wasn't explicitly in the provided context chunk. This is a common trade-off in RAG systems.

Detailed results are available in 
data/eval/benchmark_results.json
.