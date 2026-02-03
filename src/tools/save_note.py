import os
import re
from datetime import date
from pydantic_ai import RunContext
from src.models.schemas import ResearchDeps

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
