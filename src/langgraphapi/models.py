from pydantic import BaseModel, Field
from typing import Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

class HeaderModel(BaseModel):
    content_type: Annotated[str, Field(description="The media type of the body of the request", example="application/json")]

class BodyModel(BaseModel):
    pass

class QueryModel(BaseModel):
    pass

class CustomAPIInterface(BaseModel):
    request_type: Annotated[str, Field(description="HTTP method for the request", example="GET")]
    uri: Annotated[str, Field(description="The endpoint URL", example="https://www.google.com/?client=safari")]
    headers: HeaderModel
    body: BodyModel
    query: QueryModel
