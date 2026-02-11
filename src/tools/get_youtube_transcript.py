import re
from datetime import date
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic_ai import RunContext
from src.models.schemas import ResearchDeps, SearchResult

def get_youtube_transcript(ctx: RunContext[ResearchDeps], url: str) -> List[SearchResult]:
    """Extract the transcript from a YouTube video URL.
    
    Args:
        ctx: Run context.
        url: The full YouTube URL (e.g., https://www.youtube.com/watch?v=...)
    """
    print(f"  [YouTube Tool] Extracting transcript for: {url} (Limit: {ctx.deps.min_authority})")
    
    # Enforce authority constraint (YouTube = 4)
    if ctx.deps.min_authority > 4:
        print(f"  [YouTube Tool] ACCESS DENIED: Required authority {ctx.deps.min_authority} > YouTube authority 4")
        return [SearchResult(
            title="Access Denied",
            url=url,
            snippet=f"YouTube transcripts were hidden because their authority score (4) is lower than your required minimum ({ctx.deps.min_authority}).",
            date_published=date.today()
        )]
    
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
