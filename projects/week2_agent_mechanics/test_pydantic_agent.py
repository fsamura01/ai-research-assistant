import pytest
from datetime import date
from pydantic_ai import RunContext
from pydantic_ai.usage import Usage
from pydantic_ai.models.test import TestModel
from advanced_pydantic_ai import agent, perform_search, SearchQuery, SearchResult, ResearchDeps

# 1. Unit Testing a Tool
def test_perform_search_tool():
    deps = ResearchDeps(api_key="test-key")
    # Mocking the context with required fields
    ctx = RunContext(
        deps=deps, 
        retry=0, 
        tool_name="perform_search",
        model=TestModel(), 
        usage=Usage()
    )
    
    params = SearchQuery(query="pytest", max_results=1)
    results = perform_search(ctx, params)
    
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert "pytest" in results[0].title

# 2. Testing Type Validation
# We want to ensure that Pydantic catches bad data before it hits our tool.
def test_search_query_validation():
    # This should work
    q = SearchQuery(query="valid", max_results=5)
    assert q.max_results == 5
    
    # This should fail (max_results must be <= 5)
    with pytest.raises(ValueError):
        SearchQuery(query="invalid", max_results=10)

# 3. Agent Integration Testing (with TestModel)
# We don't want to call the real LLM during every test (it's slow and expensive).
# PydanticAI provides TestModel to mock the LLM's behavior.
def test_agent_logic():
    # Use TestModel to simulate the LLM choosing to call 'perform_search'
    # and then responding to the final result.
    test_model = TestModel()
    
    deps = ResearchDeps(api_key="test-key")
    
    # Run the agent using the test model
    with agent.override(model=test_model):
        user_input = "Search for python testing."
        result = agent.run_sync(user_input, deps=deps)
        
        # We can assert that the agent actually thought about the user input
        # and returned a response. Note: result.output is the primary field.
        assert result.output is not None
        print(f"\nTest Result Data: {result.output}")

# 4. Mocking Tool Calls (Advanced)
# You can also tell TestModel exactly how to behave.
def test_agent_tool_call_flow():
    # Define a sequence of responses for the LLM
    # Turn 1: LLM decides to call the tool
    # Turn 2: LLM summarizes the tool output
    test_model = TestModel()
    
    deps = ResearchDeps(api_key="test-key")
    
    with agent.override(model=test_model):
        # In a real test, you would use test_model.push_responses()
        # to simulate complex multi-turn flows.
        result = agent.run_sync("Find news", deps=deps)
        assert len(result.new_messages()) >= 1

if __name__ == "__main__":
    # Run tests using pytest logic if executed directly
    print("Running Agent Tests...")
    test_perform_search_tool()
    test_search_query_validation()
    test_agent_logic()
    print("All tests passed!")
