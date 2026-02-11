import os
import sys
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.schemas import ResearchDeps
from src.tools.save_note import save_note
from src.tools.research_local_docs import research_local_docs
from src.tools.perform_web_search import perform_web_search
from src.tools.get_youtube_transcript import get_youtube_transcript

load_dotenv()

# Initialize Model
model = GroqModel('llama-3.1-8b-instant')

# Initialize Agent
agent = Agent(
    model,
    deps_type=ResearchDeps,
)

@agent.system_prompt
def dynamic_system_prompt(ctx: RunContext[ResearchDeps]) -> str:
    min_auth = ctx.deps.min_authority
    return (
        "You are a professional AI Research Assistant. Provide evidence-based, comprehensive answers.\n"
        f"### AUTHORITY: {min_auth}/10 (GitHub:9, PDF:7, Web:5, YouTube:4)\n"
        "1. **Strict Mode**: Do not use internal knowledge or low-authority tools if threshold is high.\n\n"
        "### GAP ANALYSIS & ITERATION:\n"
        "1. Analysis: Identify 'information gaps' (e.g., if comparing Alice/Bob but you only found info on one).\n"
        "2. Loop: Perform targeted follow-up searches for missing context.\n"
        "3. **Reasoning**: Always state your gap analysis in a 'Thought:' block *before* tool calls. Never put text after a tool call in the same message."
    )

# Register Tools
agent.tool(save_note)
agent.tool(research_local_docs)
agent.tool(perform_web_search)
agent.tool(get_youtube_transcript)

if __name__ == "__main__":
    pass
