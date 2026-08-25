import logging

from app.agent.gemini_client import GeminiAgent
from app.core.exceptions import (
    GeminiUnavailableError,
    MCPUnavailableError,
    ToolInvocationError,
)
from app.fallback.parser import looks_like_multiple_calculations, parse_intent
from app.mcp.manager import MCPManager
from app.models.schemas import ChatResponse, PipelineInfo

logger = logging.getLogger(__name__)


class CalculatorService:
    def __init__(self, mcp: MCPManager, agent: GeminiAgent):
        self.mcp = mcp
        self.agent = agent

    async def chat(self, message: str) -> ChatResponse:

        if not self.mcp.connected:
            raise MCPUnavailableError()

        tools = self.mcp.tools

        allowed = {
            tool["name"]
            for tool in tools
        } & {
            "add",
            "subtract",
            "multiply",
            "divide",
        }

        if not allowed:
            raise MCPUnavailableError(
                "No calculator MCP tools are available."
            )

        # ---------------------------------------------------------
        # STEP 0: Reject multi-calculation input up front.
        #
        # Bug fix: inputs like "10 + 20 10 - 5 10 * 5 100 / 5" were
        # previously sent straight to Gemini, which sometimes produced a
        # garbled response (a partially-serialized function-call trace)
        # and silently dropped every expression but one. We now detect
        # this case deterministically before calling Gemini/the fallback
        # parser at all, and ask the user to send one calculation at a
        # time instead of guessing.
        # ---------------------------------------------------------

        if looks_like_multiple_calculations(message):
            return ChatResponse(
                response=(
                    "I can only handle one calculation at a time — "
                    "please send them one by one."
                ),
                pipeline=PipelineInfo(
                    intent="unsupported",
                    operation="none",
                    operands=[],
                    mcp_tool="none",
                    result=None,
                ),
            )

        intent = "calculation"
        selected_tool = None
        args = None

        # This will contain Gemini's ORIGINAL model Content.
        #
        # We need this later because Gemini 3 function calls
        # can contain a thought_signature.
        model_content = None

        # ---------------------------------------------------------
        # STEP 1: Ask Gemini to select the calculator tool
        # ---------------------------------------------------------

        try:
            selected_tool, args, model_content = (
                await self.agent.choose_tool(
                    message,
                    tools,
                )
            )

            if selected_tool not in allowed:
                raise ToolInvocationError(
                    "The selected calculator tool is not allowed."
                )

            logger.info(
                "Gemini selected tool: %s",
                selected_tool,
            )

        except GeminiUnavailableError:

            logger.warning(
                "Gemini unavailable; using Fallback intent parser"
            )

            parsed = parse_intent(message)

            if (
                parsed is None
                or parsed.operation not in allowed
            ):
                return ChatResponse(
                    response=(
                        "I can currently help with addition, "
                        "subtraction, multiplication, and division."
                    ),
                    pipeline=PipelineInfo(
                        intent="unsupported",
                        operation="none",
                        operands=[],
                        mcp_tool="none",
                        result=None,
                    ),
                )

            selected_tool = parsed.operation

            args = {
                "a": parsed.operands[0],
                "b": parsed.operands[1],
            }

        # ---------------------------------------------------------
        # STEP 2: Validate Gemini/fallback arguments
        # ---------------------------------------------------------

        if (
            not isinstance(args, dict)
            or "a" not in args
            or "b" not in args
        ):
            raise ToolInvocationError(
                "The calculator tool arguments were invalid."
            )

        # ---------------------------------------------------------
        # STEP 3: Execute the MCP calculator tool
        # ---------------------------------------------------------

        # BUG FIX: previously, divide-by-zero was only caught by string-
        # matching "zero" inside the exception raised by the MCP call.
        # That never actually worked: the MCP server framework catches the
        # tool's `ValueError("I can't divide by zero.")` internally and
        # re-raises it as a generic `UnexpectedToolError: Error executing
        # tool divide` -- which contains the word "divide" but NOT "zero".
        # So the string match could never match, and every "10 / 0" request
        # fell straight through to `ToolInvocationError` -> HTTP 502,
        # regardless of the (dead) safety net below.
        #
        # We now check for division by zero deterministically, before ever
        # calling the MCP tool, so the clean message no longer depends on
        # what text a third-party framework happens to preserve.
        if (
            selected_tool == "divide"
            and float(args["b"]) == 0
        ):
            return ChatResponse(
                response="I can't divide by zero.",
                pipeline=PipelineInfo(
                    intent=intent,
                    operation=selected_tool,
                    operands=[
                        float(args["a"]),
                        float(args["b"]),
                    ],
                    mcp_tool=selected_tool,
                    result=None,
                ),
            )

        try:
            result = await self.mcp.call(
                selected_tool,
                {
                    "a": float(args["a"]),
                    "b": float(args["b"]),
                },
            )

        except Exception as exc:

            message_text = str(exc)

            # Kept as a defensive fallback in case some other MCP error
            # ever does carry "zero" in its text -- but this is no longer
            # the primary defense (see the pre-check above).
            if (
                "zero" in message_text.lower()
                or "divide by zero" in message_text.lower()
            ):
                return ChatResponse(
                    response="I can't divide by zero.",
                    pipeline=PipelineInfo(
                        intent=intent,
                        operation=selected_tool,
                        operands=[
                            float(args["a"]),
                            float(args["b"]),
                        ],
                        mcp_tool=selected_tool,
                        result=None,
                    ),
                )

            logger.exception(
                "MCP tool invocation failed"
            )

            raise ToolInvocationError() from exc

        # ---------------------------------------------------------
        # STEP 4: Ask Gemini to generate the final response
        # ---------------------------------------------------------

        if model_content is not None:

            final_text = await self.agent.final_response(
                message,
                selected_tool,
                {
                    "a": float(args["a"]),
                    "b": float(args["b"]),
                },
                result,
                model_content,
            )

        else:
            # This happens when the fallback parser was used.
            #
            # In that situation there is no Gemini model Content
            # and therefore no Gemini thought_signature to preserve.
            final_text = self.agent._format_result(
                selected_tool,
                {
                    "a": float(args["a"]),
                    "b": float(args["b"]),
                },
                result,
            )

        # ---------------------------------------------------------
        # STEP 5: Return final API response
        # ---------------------------------------------------------

        return ChatResponse(
            response=final_text,
            pipeline=PipelineInfo(
                intent=intent,
                operation=selected_tool,
                operands=[
                    float(args["a"]),
                    float(args["b"]),
                ],
                mcp_tool=selected_tool,
                result=result.get("result"),
            ),
        )