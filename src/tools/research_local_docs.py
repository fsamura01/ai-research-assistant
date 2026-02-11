from datetime import date
from typing import List
from pydantic_ai import RunContext
from src.models.schemas import ResearchDeps, SearchResult

def research_local_docs(ctx: RunContext[ResearchDeps], query: str, max_results: int = 3) -> List[SearchResult]:
    """Search the user's uploaded local PDFs and files for information.
    
    Args:
        ctx: Run context.
        query: The specific topic to look up in the documents.
        max_results: Number of chunks to retrieve.
    """
    print(f"  [Retriever] Searching for: {query} (Min Authority: {ctx.deps.min_authority})")
    raw_results = ctx.deps.vector_store.search(
        query, 
        min_authority=ctx.deps.min_authority, 
        top_k=max_results
    )
    print(f"  [Retriever] Found {len(raw_results)} results.")
    
    # Map raw vector results to our structured SearchResult model
    results = []
    for r in raw_results:
        # Extract metadata, handling potential missing fields gracefully
        meta = r.get("metadata", {})
        results.append(SearchResult(
            title=meta.get("title") or meta.get("source_url") or "Unknown Document",
            url=meta.get("source_url") or "local-file",
            snippet=r["text"][:500], # Pass the chunk text as snippet
            date_published=date.today() # Placeholder as we might not have real dates for all chunks
        ))
    
    return results
