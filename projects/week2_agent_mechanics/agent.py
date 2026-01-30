import sys
import os

# Add project root to path (two levels up from projects/week2_learning_assistant/)
# sys.path.append(os.path.abspath(os.path.join('..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#print(sys.path)

from groq import Groq
from src.utils.config import Config

class Agent:
    """A simple AI agent that can answer questions"""

    def __init__(self, tools):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.system_message = "You are a helpful assistant that breaks down problems into steps and solves them systematically."
        self.messages = [
            {"role": "system", "content": self.system_message},
        ]
        self.tools = tools
        self.tool_map={tool.get_schema()['name']: tool for tool in tools}

    def _get_tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.get_schema()["name"],
                    "description": tool.get_schema()["description"],
                    "parameters": tool.get_schema()["input_schema"]
                }
            }
            for tool in self.tools
        ]

    def chat(self, message):
        """Process a user message and return a response"""
        # Add user message to history or short term memory
        self.messages.append({"role": "user", "content": message})

        while True:
            # 1. Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=self.messages,
                tools=self._get_tools_schema() if self.tools else None,
                temperature=0.1,
            )

            assistant_message = response.choices[0].message
            
            # 2. Add assistant response to history
            history_entry = {
                "role": "assistant",
                "content": assistant_message.content or ""
            }
            if assistant_message.tool_calls:
                history_entry["tool_calls"] = assistant_message.tool_calls
            
            self.messages.append(history_entry)

            # 3. Check if the LLM wants to use tools
            if not assistant_message.tool_calls:
                # No more tool calls, we are finished with this turn
                return response

            # 4. Handle tool calls
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                import json
                args = json.loads(tool_call.function.arguments)
                
                print(f"  [Executing Tool] {function_name}({args})")
                
                if function_name in self.tool_map:
                    # Execute the tool
                    result = self.tool_map[function_name].execute(**args)
                    
                    # 5. Add tool result to history (REQUIRED for the next step)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                else:
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": "Error: Tool not found"
                    })
            
            # 6. The loop continues to send tool results back to the LLM