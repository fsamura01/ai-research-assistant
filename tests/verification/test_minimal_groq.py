from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import os
from dotenv import load_dotenv

load_dotenv()

async def test_minimal():
    model = GroqModel('llama-3.3-70b-versatile')
    agent = Agent(model)
    result = await agent.run("Hello, say 'Test OK'")
    print(f"Result: {result.output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_minimal())
