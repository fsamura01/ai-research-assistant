# Implementation Plan: Week 2 - Agent Mechanics from Scratch

This week focuses on building the foundational components of an AI agent manually. By avoiding frameworks initially, we will understand how state management, tool calling, and control loops function under the hood.

**Goal**

Build a functional agent that can use tools and reason through tasks without using high-level agent frameworks (like LangChain, CrewaI, or PydanticAI).

**Proposed Changes**

## [Component Name] Project Structure
Create a new project directory for Week 2.

## [NEW] manual_agent.py
A standalone script implementing the ManualAgent logic.

## [Component Name] Manual Agent Implementation
The agent will follow the ReAct (Reasoning and Acting) pattern.

### Control Loop

- input: User query.
- loop:
    - Ask LLM for next step (Thought + Action).
    - Parse LLM response.
    - If Action is requested:
        - Execute tool.
    - Add observation to history.
    - If Final Answer is provided:
        - Return response to user.

### Tool Calling Mechanics

- Tools will be defined as simple Python functions with human-readable descriptions.
- The prompt will explicitly instruct the LLM on how to format tool calls (e.g., JSON or specific string patterns).
- Manual parsing of the LLM output to extract function names and arguments.

### Verification Plan

- Automated Tests
    - Script-based verification: Run the agent with a query that requires multiple tool calls (e.g., "What is the weather in London and what is the capital of France?").
    - Verify that the agent correctly identifies the tools and executes them in sequence.

- Manual Verification
    - Review the logs to see the step-by-step Thought, Action, and Observation cycle.



## Walkthrough: Week 2 - Agent Mechanics from Scratch
We have successfully built an agent from scratch to understand its internal mechanics and then transitioned to PydanticAI to see how frameworks abstract these complexities.

1. **Manual Agent (The "Hard" Way)**

-   We implemented a 
ManualAgent
 that follows the ReAct (Reasoning and Acting) pattern.

Core Mechanics Demonstrated:

- **System Prompt**: Explicitly teaching the LLM how to "think" and "act" using a specific format.
- **Control Loop**: A while or for loop that manages the state and sequential execution.
- **Tool Registry**: Mapping tool names to Python functions.
- **Manual Parsing**: Using Regex to extract tool names and arguments from the LLM's text output.
- **Observation Loop**: Feeding the tool output (Observation) back into the LLM's history.
manual_agent.py

**Sample Run Output:**

---
[User]: What is the weather in London, and what would it be if the temperature doubled?

--- Step 1 ---
Thought: To answer this question, I first need to find out the current weather in London.
Action: get_weather(London)
  [Tool] Calling get_weather for: London
Observation: 15°C and Cloudy

--- Step 2 ---
Thought: The current temperature in London is 15. Doubling 15... 
Action: calculator(15*2)
  [Tool] Calling calculator for: 15*2
Observation: 30

--- Step 3 ---
Thought: I have the result.
Final Answer: The weather in London is 15°C and Cloudy. If the temperature were to double, it would be 30°C.

---

2. **PydanticAI Agent (The Framework Way)**

- We implemented the same functionality using PydanticAI.

**Key Differences & Benefits:**

- Declarative Tools: Tools are registered with a simple decorator (@agent.tool).
- Automatic Orchestration: The framework handles the ReAct loop, retries, and state management automatically.
- Typed Tools: We can use Pydantic models for complex arguments, ensuring the LLM sends valid data.
- Simplified Prompts: We no longer need to explain "Thought/Action/Observation" in the prompt; the framework uses native tool calling.
pydantic_ai_agent.py

**Results & Verification**

- Both agents correctly identified the need for two sequential tool calls.
- Both agents correctly calculated the final result.
- The manual approach made the mechanics explicit, while the framework approach significantly reduced boilerplate.

**Next Steps**

- Now that we understand the foundations, we will continue Week 2 by going deeper into PydanticAI:

- Type validation for tool arguments.
- Handling complex tool outputs.
- Testing and debugging agentic flows.

**Implementation Plan: Advanced PydanticAI Features**
This phase focuses on leveraging the full power of PydanticAI for robust agent development, specifically focusing on type safety, structured data, and testability.

**Goal**
Build a "Research Assistant" that uses PydanticAI to search for information, process complex data, and demonstrate robust error handling and testing.

**Proposed Changes**

**[Component Name] Advanced Agent Implementation**
We will create a new script that showcases advanced features.

**[NEW] advanced_pydantic_ai.py**
This script will implement:

Type Validation: Use Pydantic models for tool arguments to ensure the LLM sends valid data.
Complex Outputs: Tools that return structured objects (e.g., a "Search Result" with snippets and URLs) rather than just strings.
Dependencies: Use PydanticAI's Deps to inject shared state or clients (like a search client).

**[Component Name] Testing and Debugging**
Create a dedicated test file to demonstrate how to verify agent behavior.

**[NEW] test_pydantic_agent.py**
Unit Testing Tools: Testing individual tool functions.
Agent Testing: Mocking the LLM and asserting that the agent calls the correct tools in response to specific queries.
Logfire Integration: Show how to use Logfire for debugging flows.

**Verification Plan**

**Automated Tests**
Run pytest projects/week2_agent_mechanics/test_pydantic_agent.py.
Verify that tool validation fails correctly when passed bad data.

**Manual Verification**
Run the advanced script and inspect the structured output.
Check Logfire logs (if applicable) to see the execution trace.

**Week 2 Walkthrough: Agent Mechanics & Deep Dive into PydanticAI**
We've completed the transition from a manual "from scratch" agent to a high-powered, type-safe agent using PydanticAI.

**Phase 1: The Manual Foundation**
We built a manual agent to understand the ReAct (Thought, Action, Observation) loop.

Tools: Plain Python functions.
Parsing: Manual regex to find Action: tool_name(args).
Memory: A self.messages list maintained manually.

**Phase 2: Advanced PydanticAI Features**
We implemented a ResearchAssistant that showcases industrial-grade agent design.

**1. Type Validation**
We used Pydantic models to define exactly what the LLM is allowed to send.

class SearchQuery(BaseModel):
    query: str
    max_results: int = Field(default=3, ge=1, le=5) # Hard limits!

**IMPORTANT**

This prevents "hallucinated" arguments or out-of-bounds numbers from breaking your system.

**2. Structured Tool Outputs**
Our tools now return complex objects (
SearchResult
), which PydanticAI automatically serializes for the LLM.

Benefit: The LLM gets clear, structured data (Title, URL, Snippet) rather than just a messy string.

**3. Automated Testing**
We implemented a full test suite in 
test_pydantic_agent.py
:

Unit Tests: Verifying individual tool logic.
Agent Testing: Using TestModel() to simulate LLM responses without spending money on API calls.
Verification Results
We ran the test suite across the new components:

uv run python projects/week2_agent_mechanics/test_pydantic_agent.py
Output:

test_perform_search_tool
: Passed ✅
test_search_query_validation
: Passed ✅
test_agent_logic
: Passed ✅

**Key Learnings**
Abstraction: Frameworks like PydanticAI replace complex regex and manual loops with clean decorators and types.
Reliability: Type validation makes agents significantly more stable in production.
Testability: Using TestModel allows for deterministic testing of complex agentic flows.