import asyncio
from src.langgraphapi.models import CustomAPIInterface
from src.langgraphapi.wrapper import APIWrapper
from langchain_core.messages import AIMessage, ToolCall
from langgraph.graph import StateGraph, END
import requests
from typing import List, TypedDict
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]

# Mock the requests.request function
def mock_request(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = str(json_data)

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"HTTP Error: {self.status_code}")

    return MockResponse({"data": "This is a mock API response"}, 200)

# Replace the actual request function with our mock
requests.request = mock_request

# Create the CustomAPIInterface
api_interface = CustomAPIInterface(
    method="GET",
    url="https://api.example.com/data",
    headers={"Content-Type": "application/json"},
    body=None,
    query=None
)

# Initialize the APIWrapper
api_wrapper = APIWrapper(api_interface)

# Create the main graph
main_graph = StateGraph(GraphState)

# Add the api_wrapper node
main_graph.add_node("api_wrapper", api_wrapper)

# Set up the rest of your graph
main_graph.set_entry_point("api_wrapper")
main_graph.add_edge("api_wrapper", END)

# Compile the main graph
graph = main_graph.compile()

# Create a mock state with an AI message containing tool calls
mock_state = {
    "messages": [
        AIMessage(
            content="Make an API call",
            tool_calls=[
                ToolCall(
                    id="call1",
                    type="function",
                    name="api_wrapper",
                    args={},
                )
            ]
        )
    ]
}

# Function to run the async graph
async def run_graph():
    print("Starting graph execution...")
    result = await graph.ainvoke(mock_state)
    return result

# Run the graph and print the output
if __name__ == "__main__":
    print("Initializing test...")
    result = asyncio.run(run_graph())
    print("\nGraph execution result:")
    print(result)
    
#     # Print the API response from the state
#     if 'api_wrapper' in result and 'api_result' in result['api_wrapper']:
#         print("\nAPI Response:")
#         print(result['api_wrapper']['api_result'])
#     else:
#         print("\nNo API response found in the result.")
