import os
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv
import logfire

# 1. Setup & Config
load_dotenv()
logfire.configure(send_to_logfire='never')

model = GroqModel('llama-3.3-70b-versatile')

# 2. Define Structured Data Models
# This is "Type Validation" in action. 
# We define exactly what the LLM should send to our tools.

class SearchQuery(BaseModel):
    """Schema for search queries."""
    query: str = Field(description="The search string to look up.")
    max_results: int = Field(default=3, ge=1, le=5, description="Number of results to return.")
    category: Optional[str] = Field(None, description="Optional category to filter results (e.g., 'tech', 'news').")

class SearchResult(BaseModel):
    """Schema for a single search result."""
    title: str
    url: str
    snippet: str
    date_published: date

# 3. Define Dependencies
# Deps allow us to inject "live" objects (like DB clients or API keys) 
# into tools without hardcoding them.
class ResearchDeps:
    def __init__(self, api_key: str):
        self.api_key = api_key

# 4. Initialize the Agent
agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=str, # Using output_type as per library inspection
    system_prompt=(
        "You are a sophisticated Research Assistant. "
        "Use the search tool to find information and provide structured summaries."
    ),
)

# write agent to a file
#with open('agent.txt', 'w') as f:
#    f.write(str(vars(agent)))

# 5. Advanced Tool Registration
@agent.tool
def perform_search(ctx: RunContext[ResearchDeps], params: SearchQuery) -> List[SearchResult]:
    """Perform a search for information using validated parameters.
    
    Args:
        ctx: The run context containing dependencies.
        params: The validated search parameters (Type Validation).
    """
    print(f"  [Advanced Tool] Searching for: {params.query} (Max: {params.max_results})")
    
    # In a real app, you would use ctx.deps.api_key to call a real search API (Tavily, Serper, etc.)
    # For this demo, we return mock structured data.
    
    mock_results = [
        SearchResult(
            title=f"Result 1 for {params.query}",
            url="https://example.com/1",
            snippet="This is a detailed snippet about the topic.",
            date_published=date(2024, 1, 20)
        ),
        SearchResult(
            title=f"Result 2 for {params.query}",
            url="https://example.com/2",
            snippet="Another interesting perspective on the subject.",
            date_published=date(2024, 1, 25)
        )
    ]
    
    # We return a List of Pydantic objects. 
    # PydanticAI handles the serialization back to the LLM!
    return mock_results[:params.max_results]

# 6. Main Execution
if __name__ == "__main__":
    deps = ResearchDeps(api_key="mock-key-123")
    user_input = "Find the latest news about AI agent frameworks and summarize the top 2 results."
    
    print(f"\n[User]: {user_input}")
    
    # Run the agent with dependencies
    result = agent.run_sync(user_input, deps=deps)
    
    print(f"\n[Agent Summary]:\n{result.output}")
