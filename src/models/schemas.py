from datetime import date
from typing import Optional
from pydantic import BaseModel
from tavily import TavilyClient
import os
from dotenv import load_dotenv

# Load env for Tavily
load_dotenv()

# Import VectorStore (Avoiding circular import by using TYPE_CHECKING if necessary, 
# but for runtime, we need the class. 
# Since VectorStore is in utils, and this is models, utils -> models is common, 
# but models -> utils (if VectorStore depends on models) is circular.
# VectorStore DOES NOT depend on models (it returns dicts or simple types mostly).
# So importing VectorStore here is safe.)

from src.utils.vector_store import VectorStore

class SearchResult(BaseModel):
    """Schema for a single search result."""
    title: str
    url: str
    snippet: str
    date_published: date

class ResearchDeps:
    """Dependencies for the research agent."""
    def __init__(self, api_key: str, vector_store: VectorStore = None, min_authority: int = 1):
        self.api_key = api_key
        # Initialize or use provided vector store
        self.vector_store = vector_store or VectorStore(in_memory=False)
        # Initialize Tavily client for live web search
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.min_authority = min_authority
