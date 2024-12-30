from pydantic import BaseModel, Field
from typing import Annotated, Dict, Any, Type
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
import requests
from models import CustomAPIInterface, HeaderModel, BodyModel, QueryModel

class APIInterfaceWrapper:
    def __init__(self):
        self.api_interface = None

    def define_api(self, request_type: str, uri: str, headers: Dict[str, Any], body: Dict[str, Any], query: Dict[str, Any]):
        self.api_interface = CustomAPIInterface(
            request_type=request_type,
            uri=uri,
            headers=HeaderModel(**headers),
            body=BodyModel(**body),
            query=QueryModel(**query)
        )

    def create_api_node(self, llm):
        if not self.api_interface:
            raise ValueError("API interface not defined. Call define_api() first.")

        class APINode:
            def __init__(self, api_interface, llm):
                self.api_interface = api_interface
                self.llm = llm

            async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
                filled_api_details = await self.fill_api_details(state)
                response = self.make_api_call(filled_api_details)
                state["messages"].append(AIMessage(content=f"API Response: {response}"))
                return state

            async def fill_api_details(self, state: Dict[str, Any]) -> Dict[str, Any]:
                prompt = self.create_prompt_for_api_details(state)
                llm_response = await self.llm.ainvoke(prompt)
                return self.parse_llm_response(llm_response)

            def make_api_call(self, api_details: Dict[str, Any]) -> str:
                try:
                    response = requests.request(
                        method=api_details["request_type"],
                        url=api_details["uri"],
                        headers=api_details["headers"],
                        json=api_details["body"],
                        params=api_details["query"]
                    )
                    response.raise_for_status()
                    return f"Request successful. Status code: {response.status_code}. Response: {response.text}"
                except requests.exceptions.RequestException as e:
                    return f"Request failed. Error: {str(e)}"

            def create_prompt_for_api_details(self, state: Dict[str, Any]) -> str:
                return f"""
                Based on the current conversation and the following API interface, please fill in the necessary details:

                {self.api_interface.json(indent=2)}

                Current conversation:
                {state['messages']}

                Please provide the filled API details in a structured format.
                """

            def parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
                # Implement parsing logic to extract API details from LLM response
                # This is a placeholder and should be implemented based on your LLM's output format
                pass

        return APINode(self.api_interface, llm)

    def create_api_graph(self, llm, agent_function, should_end_conversation):
        if not self.api_interface:
            raise ValueError("API interface not defined. Call define_api() first.")

        workflow = StateGraph(Dict)
        
        api_node = self.create_api_node(llm)
        
        workflow.add_node("agent", agent_function)
        workflow.add_node("api_call", api_node)
        
        workflow.add_edge("agent", "api_call")
        workflow.add_edge("api_call", "agent")
        
        workflow.add_conditional_edges(
            "agent",
            should_end_conversation,
            {
                True: END,
                False: "api_call"
            }
        )
        
        return workflow.compile()
