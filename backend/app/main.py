import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agent.gemini_client import GeminiAgent
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.mcp.manager import MCPManager
from app.services.calculator_service import CalculatorService

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp = MCPManager()
    app.state.settings = settings
    app.state.mcp = mcp
    app.state.calculator_service = CalculatorService(
        mcp,
        GeminiAgent(settings.gemini_api_key, settings.gemini_model),
    )

    try:
        await mcp.startup()
        logger.info("Application startup complete")
        yield
    finally:
        await mcp.shutdown()
        logger.info("Application shutdown complete")


app = FastAPI(
    title="Agentic Calculator API",
    version="1.0.0",
    description="Gemini-powered calculator agent using a real MCP client/server architecture.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    logger.info(
        "Request received: %s %s",
        request.method,
        request.url.path,
        extra={"request_id": request_id},
    )
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        logger.exception("Unhandled request error", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected server error occurred.",
                }
            },
            headers={"X-Request-ID": request_id},
        )


app.include_router(router)
