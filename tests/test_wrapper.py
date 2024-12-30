import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import Tool
from langgraph.prebuilt import ToolNode

from src.langgraphapi.wrapper import APIInterfaceWrapper

# Mock LLM for testing
class MockLLM:
    async def ainvoke(self, prompt):
        return '{"request_type": "GET", "uri": "https://api.example.com/data", "headers": {"Authorization": "Bearer token"}, "body": {}, "query": {"param": "value"}}'

# Mock tool for testing
def mock_tool(request_type, uri, headers, body, query):
    return f"Mock API call: {request_type} {uri}"

# Create a test tool
test_tool = Tool(
    name="test_api",
    func=mock_tool,
    description="A test API tool"
)

@pytest.fixture
def api_wrapper():
    return APIInterfaceWrapper()

def test_define_api(api_wrapper):
    api_wrapper.define_api(
        request_type="GET",
        uri="https://api.example.com/data",
        headers={"Authorization": {"description": "Bearer token", "example": "Bearer abc123"}},
        body={},
        query={"param": {"description": "Query parameter", "example": "value"}}
    )
    assert api_wrapper.api_interface is not None
    assert api_wrapper.api_interface.request_type == "GET"
    assert api_wrapper.api_interface.uri == "https://api.example.com/data"

@pytest.mark.asyncio
async def test_create_api_node(api_wrapper):
    api_wrapper.define_api(
        request_type="GET",
        uri="https://api.example.com/data",
        headers={"Authorization": {"description": "Bearer token", "example": "Bearer abc123"}},
        body={},
        query={"param": {"description": "Query parameter", "example": "value"}}
    )
    
    mock_llm = MockLLM()
    api_node = api_wrapper.create_api_node(mock_llm)
    
    state = {
        "messages": [
            HumanMessage(content="Make an API call"),
            AIMessage(content="Certainly! I'll make an API call for you.", tool_calls=[
                {"name": "test_api", "id": "call1", "type": "function", "args": {}}
            ])
        ]
    }
    
    result = await api_node(state)
    assert isinstance(result, dict)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0].content.startswith("Mock API call: GET https://api.example.com/data")

def test_create_api_graph(api_wrapper):
    api_wrapper.define_api(
        request_type="GET",
        uri="https://api.example.com/data",
        headers={"Authorization": {"description": "Bearer token", "example": "Bearer abc123"}},
        body={},
        query={"param": {"description": "Query parameter", "example": "value"}}
    )
    
    mock_llm = MockLLM()
    mock_agent = lambda x: x
    mock_should_end = lambda x: "__end__"
    
    graph = api_wrapper.create_api_graph(mock_llm, mock_agent, mock_should_end)
    assert graph is not None

if __name__ == "__main__":
    pytest.main([__file__])
