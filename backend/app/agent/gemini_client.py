import asyncio
import logging
import re
from typing import Any

from google import genai
from google.genai import types

from app.core.exceptions import GeminiUnavailableError
from app.agent.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Bug fix: the tool declarations passed to Gemini are plain
# `types.FunctionDeclaration` objects (not real Python callables), so the
# SDK's Automatic Function Calling (AFC) can never actually execute anything
# here -- but the SDK still emits a noisy warning on every call and, per
# Google's own docs, direct use of AFC via `Models.generate_content` is
# "not recommended". We disable it explicitly on every config to remove the
# warning and any related nondeterminism.
_AFC_DISABLED = types.AutomaticFunctionCallingConfig(disable=True)

# Bug fix: Gemini's free-form final-response text occasionally echoed the
# raw tool-result object or an internal function-call trace instead of a
# plain sentence (e.g. `{ "operation": "multiply", ... }` or
# `default_api:subtract{result:{...}}`). If the text looks like that, we
# discard it and fall back to our own deterministic formatter instead of
# showing it to the user.
_SUSPICIOUS_TEXT_PATTERNS = (
    re.compile(r'"operation"\s*:'),
    re.compile(r"\bdefault_api\b"),
    re.compile(r"[{}]"),
)


def _looks_like_raw_payload(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SUSPICIOUS_TEXT_PATTERNS)


class GeminiAgent:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.enabled = bool(api_key)
        self.client = genai.Client(api_key=api_key) if self.enabled else None

    @staticmethod
    def _mcp_to_gemini_tools(mcp_tools: list[dict]) -> list[types.Tool]:
        declarations = []

        for tool in mcp_tools:
            schema = dict(tool.get("input_schema") or {})
            schema.pop("$schema", None)

            declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters_json_schema=schema,
                )
            )

        return [types.Tool(function_declarations=declarations)]

    async def choose_tool(
        self,
        message: str,
        mcp_tools: list[dict],
    ) -> tuple[str, dict[str, Any], Any]:

        if not self.enabled or self.client is None:
            raise GeminiUnavailableError("Gemini API key is not configured.")

        tools = self._mcp_to_gemini_tools(mcp_tools)

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools,
            temperature=0,
            automatic_function_calling=_AFC_DISABLED,
        )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model,
                    contents=message,
                    config=config,
                ),
                timeout=20,
            )

        except Exception as exc:
            logger.exception(
                "Gemini tool-selection request failed: %s",
                type(exc).__name__,
            )
            raise GeminiUnavailableError() from exc

        function_call = self._find_function_call(response)

        if not function_call:
            raise GeminiUnavailableError(
                "Gemini did not select a supported calculator tool."
            )

        name = getattr(function_call, "name", None)
        args = getattr(function_call, "args", None) or {}

        if not name or not isinstance(args, dict):
            raise GeminiUnavailableError(
                "Gemini returned an invalid tool request."
            )

        # IMPORTANT:
        # Preserve Gemini's original model Content.
        #
        # Gemini 3 function calls can contain a thought_signature.
        # We must send this original Content back to Gemini instead
        # of reconstructing the function_call manually.
        model_content = None

        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)

            if content is not None:
                for part in getattr(content, "parts", []) or []:
                    if getattr(part, "function_call", None):
                        model_content = content
                        break

            if model_content is not None:
                break

        if model_content is None:
            raise GeminiUnavailableError(
                "Gemini returned a function call without model content."
            )

        return name, args, model_content

    async def final_response(
        self,
        message: str,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_result: dict[str, Any],
        model_content: Any,
    ) -> str:

        if not self.enabled or self.client is None:
            return self._format_result(
                tool_name,
                tool_args,
                tool_result,
            )

        # Create the response from the MCP tool.
        tool_response = types.Part.from_function_response(
            name=tool_name,
            response=tool_result,
        )

        # IMPORTANT:
        # Do NOT reconstruct the Gemini function call with:
        #
        # types.Part.from_function_call(...)
        #
        # because that loses Gemini 3's thought_signature.
        #
        # Instead, reuse the exact model Content returned by Gemini.
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=message),
                ],
            ),
            model_content,
            types.Content(
                role="user",
                parts=[
                    tool_response,
                ],
            ),
        ]

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
            automatic_function_calling=_AFC_DISABLED,
        )

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model,
                    contents=contents,
                    config=config,
                ),
                timeout=20,
            )

            text = (getattr(response, "text", None) or "").strip()

            if text and not _looks_like_raw_payload(text):
                return text

            if text:
                logger.warning(
                    "Discarding Gemini final-response text that looked like "
                    "a raw payload/function-call trace instead of a plain "
                    "sentence."
                )

        except Exception as exc:
            logger.exception(
                "Gemini final-response request failed: %s",
                type(exc).__name__,
            )

        # Gemini final response is optional.
        # If it fails, still return a correct calculator result.
        return self._format_result(
            tool_name,
            tool_args,
            tool_result,
        )

    @staticmethod
    def _find_function_call(response: Any) -> Any | None:
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)

            for part in getattr(content, "parts", []) or []:
                call = getattr(part, "function_call", None)

                if call:
                    return call

        return None

    @staticmethod
    def _format_number(x: Any) -> str:
        """Format a number consistently, without ever switching to
        scientific notation (bug fix: the previous `:g` formatting turned
        e.g. 1_000_000.0 into "1e+06"). Whole numbers show no decimal
        point; fractional numbers keep up to 10 significant decimal
        places with trailing zeros trimmed. Thousands separators are used
        throughout so results look the same regardless of size.
        """
        if not isinstance(x, (int, float)):
            return str(x)

        if float(x).is_integer():
            return f"{int(x):,}"

        text = f"{x:,.10f}".rstrip("0").rstrip(".")
        return text

    @staticmethod
    def _format_result(
        tool_name: str,
        args: dict[str, Any],
        result: dict[str, Any],
    ) -> str:

        a = args.get("a")
        b = args.get("b")
        value = result.get("result")

        symbols = {
            "add": "+",
            "subtract": "−",
            "multiply": "×",
            "divide": "÷",
        }

        symbol = symbols.get(tool_name, tool_name)

        if value is not None:
            if all(
                isinstance(x, (int, float))
                for x in (a, b, value)
            ):
                fmt = GeminiAgent._format_number
                return f"{fmt(a)} {symbol} {fmt(b)} = {fmt(value)}"

            return f"{a} {symbol} {b} = {value}"

        return str(result)