Week 2 Final Walkthrough: Agent Mechanics & Real Tool Integration
We have successfully built a production-ready Agentic Research Assistant.

What We Built
We moved from a manual "Thought/Action/Observation" loop to a sophisticated agent powered by PydanticAI.

1. The Core Brain
Our agent now uses llama-3.3-70b (via Groq) to orchestrate complex research tasks. It follows strict system prompts to decide which tool to use.

2. The Integrated "Hands" (Real Tools)
The agent is no longer mocking its abilities. It is connected to:

Real Vector Search: Queries the Qdrant database we built in Week 1 to find your local documents.
Real Web Search: Uses the Tavily API to find current news and "live" information from the internet.
YouTube Transcripts: Uses youtube-transcript-api to "read" video content provided via URL.
Persistence: A 
save_note
 tool that writes findings into local Markdown files in the research_notes/ directory.
3. Safety & Robustness
Type Validation: Every tool argument is validated by Pydantic. If the LLM tries to send a string when we expect a number, it's caught and corrected.
Dependency Injection: API keys and database clients are passed safely through RunContext.
Verification
Verified: The agent can successfully search the web, summarize findings, and save them to a file.
Tests: 
test_pydantic_agent.py
 provides a suite for mocking and verifying agentic flows without spending API credits.
How to Run
Ensure your 
.env
 has GROQ_API_KEY and TAVILY_API_KEY.
Run the assistant:
uv run projects/week2_agent_mechanics/advanced_pydantic_ai.py
Check the research_notes/ folder for your saved research!
Week 2 Complete! We are now ready for Week 3: Evaluation and Monitoring.