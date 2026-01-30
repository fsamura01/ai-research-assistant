import os
import json
import re
from typing import List, Dict, Any, Callable
from groq import Groq
from dotenv import load_dotenv

# 1. Setup & Config
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Tool Definitions
# We define tools as simple Python functions.
def get_weather(location: str) -> str:
    """Get the current weather in a given location."""
    print(f"  [Tool] Calling get_weather for: {location}")
    # In a real app, this would call an API.
    responses = {
        "london": "15°C and Cloudy",
        "new york": "22°C and Sunny",
        "tokyo": "18°C and Rainy"
    }
    return responses.get(location.lower(), "Weather information not available for this location.")

def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    print(f"  [Tool] Calling calculator for: {expression}")
    try:
        # NOTE: eval is dangerous in production, but fine for this scratch implementation.
        # We use a limited set of allowed characters for a bit of safety.
        if not re.match(r"^[0-9+\-*/().\s]+$", expression):
            return "Error: Invalid expression"
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

# 3. Tool Registry
# We need a way to look up functions and describe them to the LLM.
tools: Dict[str, Dict[str, Any]] = {
    "get_weather": {
        "func": get_weather,
        "description": "Get the current weather in a given location. Argument: location (string)"
    },
    "calculator": {
        "func": calculator,
        "description": "Evaluate a mathematical expression. Argument: expression (string)"
    }
}

# 4. System Prompt
# Crucially, we must tell the LLM HOW to use these tools.
SYSTEM_PROMPT = f"""
You are a helpful assistant that can use tools. 
You follow the ReAct pattern: Thought, Action, Observation, Thought... Final Answer.

Available Tools:
{chr(10).join([f"- {name}: {info['description']}" for name, info in tools.items()])}

FORMAT RULES:
1. Thinking: Start with "Thought: " followed by your reasoning.
2. acting: To use a tool, use the format: 
   Action: tool_name(argument)
   Example: Action: calculator(2+2)
3. Observing: After an Action, you will receive an "Observation: ". Use this to continue your reasoning.
4. Final Answer: When you have the final answer, start with "Final Answer: ".

IMPORTANT: 
- You MUST use the calculator tool for any math, even simple ones.
- Only call ONE action at a time.

Example:
User: What is 15 * 12?
Thought: I need to calculate 15 multiplied by 12.
Action: calculator(15*12)
Observation: 180
Thought: I have the result.
Final Answer: 15 * 12 is 180.
"""

class ManualAgent:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def run(self, user_input: str, max_steps: int = 5):
        print(f"\n[User]: {user_input}")
        self.messages.append({"role": "user", "content": user_input})

        for step in range(max_steps):
            print(f"\n--- Step {step + 1} ---")
            
            # 5. Call LLM
            response = client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            content = response.choices[0].message.content
            print(f"\ncontent: {content}")
            
            self.messages.append({"role": "assistant", "content": content})

            # 6. Parse for Action
            # Look for "Action: tool_name(arg)"
            match = re.search(r"Action:\s*(\w+)\((.*)\)", content)
            
            if match:
                tool_name = match.group(1).strip()
                tool_arg = match.group(2).strip()
                
                # Check if tool exists
                if tool_name in tools:
                    # Execute tool
                    observation = tools[tool_name]["func"](tool_arg)
                    print(f"Observation: {observation}")
                    
                    # Add observation back to memory
                    self.messages.append({"role": "user", "content": f"Observation: {observation}"})
                else:
                    error_msg = f"Error: Tool '{tool_name}' not found."
                    print(f"Observation: {error_msg}")
                    self.messages.append({"role": "user", "content": f"Observation: {error_msg}"})
            
            # 7. Check for Final Answer
            if "Final Answer:" in content:
                print("\n[Agent]: Completed task.")
                return content

        print("\n[Agent]: Reached maximum steps without a final answer.")
        return "Task incomplete."

# 8. Main Execution
if __name__ == "__main__":
    agent = ManualAgent()
    
    # Simple query
    # agent.run("What is 25 * 4?")
    
    # Complex query requiring tools
    agent.run("What is the weather in London, and what would it be if the temperature doubled?")
