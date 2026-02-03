import os
import sys
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv
import logfire
from tavily import TavilyClient
from youtube_transcript_api import YouTubeTranscriptApi
import re

# 1. Setup & Config
# Add project root to path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

load_dotenv()
logfire.configure(send_to_logfire='never')

model = GroqModel('llama-3.3-70b-versatile')

# 2. Define Structured Data Models
# 2. Define Structured Data Models

class SearchResult(BaseModel):
    """Schema for a single search result."""
    title: str
    url: str
    snippet: str
    date_published: date

from src.vector_store import VectorStore

# 3. Define Dependencies
class ResearchDeps:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize the real vector store (persistent mode to read Week 1 data)
        self.vector_store = VectorStore(in_memory=False)
        # Initialize Tavily client for live web search
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 4. Initialize the Agent
agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=str,
    system_prompt=(
        "You are an AI Research Assistant with access to local documents (PDFs), web search, and YouTube. "
        "1. For questions about local files, PDFs, or Docker, USE 'research_local_docs'. "
        "2. For general news, USE 'perform_web_search'. "
        "When you need to use a tool, simply call it. Do not output raw JSON or XML."
        "Summarize your findings clearly for the user."
    ),
)

# 5. Tool Registration
@agent.tool
def save_note(ctx: RunContext[ResearchDeps], title: str, content: str) -> str:
    """Save a research note or summary to a local markdown file.
    
    Args:
        ctx: Run context.
        title: The title of the note (will be used as filename).
        content: The actual markdown content to save.
    """
    print(f"  [Note Tool] Saving note: {title}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs("research_notes", exist_ok=True)
        
        # Sanitize filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
        path = os.path.join("research_notes", f"{filename}.md")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nDate: {date.today()}\n\n{content}")
        
        return f"Note successfully saved to {path}"
    except Exception as e:
        return f"Error saving note: {e}"

@agent.tool
def research_local_docs(ctx: RunContext[ResearchDeps], query: str, max_results: int = 3) -> List[SearchResult]:
    """Search the user's uploaded local PDFs and files for information.
    
    Args:
        ctx: Run context.
        query: The specific topic to look up in the documents.
        max_results: Number of chunks to retrieve.
    """
    print(f"  [Retriever] Searching for: {query}")
    raw_results = ctx.deps.vector_store.search(query, top_k=max_results)
    
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

@agent.tool
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

@agent.tool
def get_youtube_transcript(ctx: RunContext[ResearchDeps], url: str) -> List[SearchResult]:
    """Extract the transcript from a YouTube video URL.
    
    Args:
        ctx: Run context.
        url: The full YouTube URL (e.g., https://www.youtube.com/watch?v=...)
    """
    print(f"  [YouTube Tool] Extracting transcript for: {url}")
    
    try:
        # Extract video ID
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if not video_id_match:
            return []
        
        video_id = video_id_match.group(1)
        
        # Fetch transcript using the pattern working in document_loader.py
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        full_text = " ".join([t.text for t in transcript_list])
        
        # Return as a SearchResult for consistent handling
        return [SearchResult(
            title=f"YouTube Transcript: {video_id}",
            url=url,
            snippet=full_text[:4000], # Increased snippet size for better research
            date_published=date.today()
        )]
    except Exception as e:
        print(f"  [YouTube Tool] Error: {e}")
        return []

# 6. Main Execution
if __name__ == "__main__":
    deps = ResearchDeps(api_key="mock-key-123")
    user_input = "What can you tell me about Docker in my local documents?"
    #user_input = "What can you tell me about the youtube transcript of the video https://www.youtube.com/watch?v=fqMOX6JJhGo?"
    #user_input = "What are the docs about Neural Networks?"

    # user_input = "Search the web for the latest AI agent frameworks, and save a summary as a note."
    # user_input = input("Enter your query: ")
    
    print(f"\n[User]: {user_input}")
    
    result = agent.run_sync(user_input, deps=deps)
    
    print(f"\n[Agent Summary]:\n{result.output}")
