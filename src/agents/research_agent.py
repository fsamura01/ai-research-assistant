import os
import sys
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import logfire
from dotenv import load_dotenv

# Add project root to path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.schemas import ResearchDeps
from src.tools.save_note import save_note
from src.tools.research_local_docs import research_local_docs
from src.tools.perform_web_search import perform_web_search
from src.tools.get_youtube_transcript import get_youtube_transcript

load_dotenv()
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic() # Instrument Pydantic models (including PydanticAI agents)

# Initialize Model
model = GroqModel('llama-3.3-70b-versatile')

# Initialize Agent
agent = Agent(
    model,
    deps_type=ResearchDeps,
    output_type=str,
    system_prompt=(
        "You are a professional AI Research Assistant. Your goal is to provide accurate, "
        "evidence-based answers by leveraging your available tools.\n\n"
        "### Guidelines:\n"
        "1. **Information Gathering**: If you don't have the answer in your current context, use the appropriate tool.\n"
        "### Process Flow:\n"
        "1. **Step 1: Search**: Use `research_local_docs` (for Docker/PDFs) or `perform_web_search` (for current events/general info).\n"
        "2. **Step 2: Analysis**: Wait for the tool results to return to you.\n"
        "3. **Step 3: Save (Optional)**: ONLY call `save_note` AFTER you have received facts. "
        "The `content` field must contain the ACTUAL ANALYZED DATA. Never use placeholders like "
        "'Summary will be provided' or 'Results will be analyzed'. If you don't have facts yet, SEARCH FIRST."
    ),
)

# Register Tools
agent.tool(save_note)
agent.tool(research_local_docs)
agent.tool(perform_web_search)
agent.tool(get_youtube_transcript)

if __name__ == "__main__":
    # Test execution
    deps = ResearchDeps(api_key="mock-key-123")
    user_input = "What can you tell me about local Docker documents?"
    
    print(f"\n[User]: {user_input}")
    
    try:
        result = agent.run_sync(user_input, deps=deps)
        print(f"\n[Agent Summary]:\n{result.output}")
    except Exception as e:
        print(f"Error running agent: {e}")
