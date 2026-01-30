import os
from typing import Dict, Any
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv
import logfire

# 1. Setup & Config
load_dotenv()
logfire.configure(send_to_logfire='never') # Disable sending to logfire for this demo

model = GroqModel('llama-3.3-70b-versatile')

# 2. Define the Agent
# Note how the system prompt is much simpler because the framework handles the ReAct logic.
agent = Agent(
    model,
    system_prompt="You are a helpful assistant that can use tools. Use them whenever necessary.",
)

# write agent output to a file
#with open("pydantic_ai_agent_output.txt", "w") as f:
#    f.write(str(dir(agent)))

# 3. Tool Registration
# In PydanticAI, tools are just functions decorated with @agent.tool.
# Docstrings are used as tool descriptions for the LLM.
@agent.tool
def get_weather(ctx: RunContext[None], location: str) -> str:
    """Get the current weather in a given location.
    
    Args:
        location: The city or location to get weather for.
    """
    print(f"  [PydanticAI Tool] Calling get_weather for: {location}")
    responses = {
        "london": "15°C and Cloudy",
        "new york": "22°C and Sunny",
        "tokyo": "18°C and Rainy"
    }
    return responses.get(location.lower(), "Weather information not available for this location.")

@agent.tool
def calculator(ctx: RunContext[None], expression: str) -> str:
    """Evaluate a mathematical expression.
    
    Args:
        expression: A valid Python math expression (e.g., '2 + 2').
    """
    print(f"  [PydanticAI Tool] Calling calculator for: {expression}")
    try:
        # PydanticAI handles the parsing and execution.
        return str(eval(expression, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Main Execution
if __name__ == "__main__":
    user_input = "What is the weather in London, and what would it be if the temperature doubled?"
    print(f"\n[User]: {user_input}")
    
    # Run the agent. 
    result = agent.run_sync(user_input)
    
    print("\n--- Full Result Object ---")
    print(result)
    print("--------------------------")
    
    # We can also see the tool calls that were made
    print("\n[Usage Details]:")
    print(f"Total steps: {len(result.new_messages())}")
