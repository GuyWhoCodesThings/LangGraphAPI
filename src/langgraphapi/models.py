from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import Dict, Optional

class APIField(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_required(cls, values):
        if values.value is None and values.description is None:
            raise ValueError("At least one of 'value' or 'description' must be provided.")
        return values

class CustomAPIInterface(BaseModel):
    method: str = Field(..., description="HTTP method for the API request (e.g., GET, POST, PUT, DELETE)")
    url: HttpUrl = Field(..., description="Full URL of the API endpoint")
    headers: Dict[str, APIField] = Field(default_factory=dict, description="HTTP headers for the request")
    body: Optional[Dict[str, APIField]] = Field(None, description="Request body for POST, PUT, or PATCH requests")
    query: Optional[Dict[str, APIField]] = Field(None, description="Query parameters for the request")

    class Config:
        validate_assignment = True
