from datetime import date
from typing import List
from pydantic_ai import RunContext
from src.models.schemas import ResearchDeps, SearchResult

def perform_web_search(ctx: RunContext[ResearchDeps], query: str, max_results: int = 3) -> List[SearchResult]:
    """Search the live internet for news and real-time updates.
    
    Args:
        ctx: Run context.
        query: The search query for the internet.
        max_results: Number of websites to check.
    """
    print(f"  [Web Search] Searching for: {query}")
    response = ctx.deps.tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced"
    )
    
    # Map Tavily results to our SearchResult model
    results = []
    for r in response.get("results", []):
        results.append(SearchResult(
            title=r["title"],
            url=r["url"],
            snippet=r["content"],
            date_published=date.today() # Tavily doesn't always provide a clear date
        ))
    
    return results
