from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty.")
        return value


class PipelineInfo(BaseModel):
    intent: str
    operation: str
    operands: list[float]
    mcp_tool: str
    result: Any = None


class ChatResponse(BaseModel):
    response: str
    pipeline: PipelineInfo


class ToolInfo(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    gemini: str
    mcp: str


class McpStatusResponse(BaseModel):
    connected: bool
    server: str
    tool_count: int


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
