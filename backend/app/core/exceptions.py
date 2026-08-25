class AppError(Exception):
    """Base application error."""

    def __init__(self, code: str, message: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class GeminiUnavailableError(AppError):
    def __init__(self, message: str = "Gemini is temporarily unavailable."):
        super().__init__("GEMINI_UNAVAILABLE", message, 503)


class MCPUnavailableError(AppError):
    def __init__(self, message: str = "Calculator service is temporarily unavailable."):
        super().__init__("MCP_UNAVAILABLE", message, 503)


class ToolInvocationError(AppError):
    def __init__(self, message: str = "The calculator tool could not be executed."):
        super().__init__("MCP_TOOL_ERROR", message, 502)
