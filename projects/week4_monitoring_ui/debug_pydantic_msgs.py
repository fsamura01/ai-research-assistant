import os
import sys
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.messages import ModelRequest, ModelResponse, ToolCall

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.schemas import ResearchDeps

def check_messages():
    model = GroqModel('llama-3.3-70b-versatile')
    agent = Agent(model, deps_type=ResearchDeps)
    
    @agent.tool_plain
    def get_weather(location: str) -> str:
        return f"The weather in {location} is sunny."

    deps = ResearchDeps(api_key="mock")
    result = agent.run_sync("What is the weather in London?", deps=deps)
    
    print(f"Result Output: {result.output}")
    print("\n--- Messages ---")
    for i, msg in enumerate(result.new_messages()):
        print(f"Message {i}: {type(msg)}")
        if isinstance(msg, ModelResponse):
            for p_idx, part in enumerate(msg.parts):
                print(f"  Part {p_idx}: {type(part)}")
                if isinstance(part, ToolCall):
                    print(f"    Tool Name: {part.tool_name}")

if __name__ == "__main__":
    check_messages()
