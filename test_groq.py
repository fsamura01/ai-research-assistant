import os
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from dotenv import load_dotenv

load_dotenv()
model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)

result = agent.run_sync("Say hello!")
print(f"Result: {result.output}")
