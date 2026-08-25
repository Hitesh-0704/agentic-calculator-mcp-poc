import logging
from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import AppError
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    McpStatusResponse,
    ToolInfo,
)
from app.services.calculator_service import CalculatorService

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def get_service(request: Request) -> CalculatorService:
    return request.app.state.calculator_service


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    mcp = request.app.state.mcp
    return HealthResponse(
        status="ok",
        gemini="configured" if settings.gemini_api_key else "not_configured",
        mcp="connected" if mcp.connected else "disconnected",
    )


@router.get("/mcp/status", response_model=McpStatusResponse)
async def mcp_status(request: Request) -> McpStatusResponse:
    mcp = request.app.state.mcp
    return McpStatusResponse(
        connected=mcp.connected,
        server="calculator-mcp-server",
        tool_count=len(mcp.tools),
    )


@router.get("/mcp/tools")
async def mcp_tools(request: Request) -> dict:
    mcp = request.app.state.mcp
    return {"tools": [ToolInfo(**tool).model_dump() for tool in mcp.tools]}


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    service = get_service(request)
    try:
        return await service.chat(payload.message)
    except AppError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc
