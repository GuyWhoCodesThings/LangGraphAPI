from typing import Dict, Any, ClassVar
from pydantic import BaseModel, Field
from .models import CustomAPIInterface
import requests
from langchain.tools import BaseTool
from langchain_core.messages import ToolMessage

class APICallerState(BaseModel):
    api_details_retrieved: bool = False
    api_details: Dict[str, Any] = {}

class APICallerInput(BaseModel):
    action: str = Field(..., description="The action to perform: 'get_api_details' or 'fill_and_request'")
    headers: Dict[str, Any] = Field(default={}, description="Headers for the API request")
    body: Dict[str, Any] = Field(default={}, description="Body for the API request")
    query: Dict[str, Any] = Field(default={}, description="Query parameters for the request")

class APICallerTool(BaseTool):
    name: ClassVar[str] = "api_caller"
    description: ClassVar[str] = "Call an API to retrieve information or perform actions"
    args_schema: ClassVar[type] = APICallerInput
    api_interface: CustomAPIInterface = Field(..., description="The API interface to use")
    state: APICallerState = Field(default_factory=APICallerState)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, api_interface: CustomAPIInterface, **kwargs):
        super().__init__(api_interface=api_interface, **kwargs)

    def get_api_details(self) -> CustomAPIInterface:
        """
        Return the details of the API interface as pydantic model.
        """
        self.state.api_details_retrieved = True
        return self.api_interface
    
    def fill_and_request(self, headers: Dict[str, Any], body: Dict[str, Any], query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill in the API fields and make the request.
        """
        # Fill in the fields
        for key, value in headers.items():
            if key in self.api_interface.headers and value not in self.api_interface.headers[key]:
                self.api_interface.headers[key].value = value

        if self.api_interface.body:
            for key, value in body.items():
                if key in self.api_interface.body and value not in self.api_interface.body[key]:
                    self.api_interface.body[key].value = value

        if self.api_interface.query:
            for key, value in query.items():
                if key in self.api_interface.query and value not in self.api_interface.query[key]:
                    self.api_interface.query[key].value = value

        # Make the request
        filled_headers = {k: v.value for k, v in self.api_interface.headers.items() if v.value is not None}
        filled_body = {k: v.value for k, v in self.api_interface.body.items() if v.value is not None} if self.api_interface.body else None
        filled_query = {k: v.value for k, v in self.api_interface.query.items() if v.value is not None} if self.api_interface.query else None

        try:
            response = requests.request(
                method=self.api_interface.method,
                url=str(self.api_interface.url),
                headers=filled_headers,
                json=filled_body,
                params=filled_query
            )
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text
            }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _run(self, action: str, headers: Dict[str, Any] = {}, body: Dict[str, Any] = {}, query: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        This method is called when the tool is invoked.
        """
        if action == "get_api_details":
            return self.get_api_details()
        elif action == "fill_and_request":
            return self.fill_and_request(headers, body, query)
        else:
            return {"error": "Invalid action. Use 'get_api_details' or 'fill_and_request'."}

    async def _arun(self, action: str, headers: Dict[str, Any] = {}, body: Dict[str, Any] = {}, query: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Asynchronous version of _run. For simplicity, it just calls the synchronous version.
        """
        return self._run(action, headers, body, query)
