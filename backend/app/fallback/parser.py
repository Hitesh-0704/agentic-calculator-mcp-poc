"""Fallback intent parser.

This parser DOES NOT calculate anything.
It only extracts an operation and two operands so the real MCP tool can run.

IMPORTANT (bug fix):
The original version of this parser only matched natural-language wording
("add 3 and 4", "subtract 18 from 50", ...). It had NO support at all for
plain symbolic expressions such as "2 + 5", "100 - 27", "-10 + -20", or
"1.5 + 2.5". Whenever Gemini was unavailable (quota exhausted / timeout)
and the fallback parser kicked in, those symbolic inputs silently fell
through to `return None`, which the caller turns into the generic
"I can currently help with addition, subtraction, ..." message. That is
the root cause of the "sometimes 2 + 5 works, sometimes it doesn't"
inconsistency: it never actually depended on the parser being flaky, it
depended entirely on whether Gemini happened to be up at that moment.

This version adds explicit symbolic-expression support and normalizes
Unicode math symbols (×, ÷, −) to their ASCII equivalents first.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedIntent:
    operation: str
    operands: tuple[float, float]


NUMBER = r"(-?\d+(?:\.\d+)?)"

_UNICODE_OPERATORS = {
    "\u2212": "-",  # minus sign
    "\u00d7": "*",  # multiplication sign
    "\u00f7": "/",  # division sign
}

_SYMBOLIC_OP_TO_OPERATION = {
    "+": "add",
    "-": "subtract",
    "*": "multiply",
    "/": "divide",
}

# Matches exactly ONE symbolic arithmetic expression, e.g. "10 + 20",
# "-5*-5", "100.25 + 50.75". Deliberately anchored so that inputs with
# more than one expression (e.g. "10 + 20 10 - 5 10 * 5") do NOT match
# here and instead fall through to the "unsupported" response, rather
# than silently being mangled into a single (wrong) operation.
_SYMBOLIC_EXPRESSION = re.compile(
    rf"^\s*{NUMBER}\s*([+\-*/])\s*{NUMBER}\s*$"
)

# A conservative check for whether a message contains more than one
# arithmetic expression at all (symbolic or worded). Used to short-circuit
# multi-calculation input with a clean message instead of letting it reach
# Gemini/the fallback parser and produce garbled output.
_MULTI_EXPRESSION_HINT = re.compile(
    rf"{NUMBER}\s*[+\-*/]\s*{NUMBER}.*{NUMBER}\s*[+\-*/]\s*{NUMBER}"
)


def looks_like_multiple_calculations(message: str) -> bool:
    """True if the message appears to contain more than one calculation."""
    normalized = _normalize_symbols(message)
    return bool(_MULTI_EXPRESSION_HINT.search(normalized))


def _normalize_symbols(message: str) -> str:
    text = message
    for unicode_char, ascii_char in _UNICODE_OPERATORS.items():
        text = text.replace(unicode_char, ascii_char)
    # The word "zero" shows up constantly in divide-by-zero phrasing
    # ("divide 50 by zero", "what is 10 divided by zero?") but the NUMBER
    # regex only matches digits. Normalize the standalone word so those
    # phrasings parse the same as "divide 50 by 0". Deliberately narrow
    # (just this one word) rather than a full spelled-number parser, which
    # is out of scope here.
    text = re.sub(r"\bzero\b", "0", text, flags=re.IGNORECASE)
    return text


def parse_intent(message: str) -> ParsedIntent | None:
    normalized = _normalize_symbols(message)
    text = " ".join(normalized.lower().split())

    # Reject multi-calculation input outright rather than guessing.
    if looks_like_multiple_calculations(normalized):
        return None

    # --- Symbolic expressions: "2 + 5", "100-27", "-10 + -20", etc. ---
    m = _SYMBOLIC_EXPRESSION.match(normalized.strip())
    if m:
        a = float(m.group(1))
        op = m.group(2)
        b = float(m.group(3))
        return ParsedIntent(_SYMBOLIC_OP_TO_OPERATION[op], (a, b))

    # --- Natural-language phrasing rules ---
    # Checked as an ordered list of (operation, regex, operand_order) rules.
    # operand_order is "ab" (group1 op group2, as written) or "ba" (the
    # second-mentioned number is really the first operand, e.g. "subtract
    # 18 from 50" means 50 - 18).
    #
    # IMPORTANT: this list intentionally covers BOTH keyword-first phrasing
    # ("divide 100 by 4") and number-first phrasing ("100 divided by 4",
    # "100 divide 4"), plus the "of"/"between" idioms ("sum of X and Y",
    # "difference between X and Y", "product of X and Y", "quotient of X
    # and Y"). A live test pass against this exact server found that only
    # the keyword-first forms were previously supported, so number-first
    # phrasing (very common in natural speech, e.g. "100 divided by 0")
    # silently fell through to "unsupported" whenever Gemini was down and
    # this fallback parser was the only thing running. That gap is closed
    # here and pinned down with regression tests.
    for operation, pattern, operand_order in _NL_RULES:
        m = re.search(pattern, text)
        if m:
            first, second = float(m.group(1)), float(m.group(2))
            if operand_order == "ba":
                first, second = second, first
            return ParsedIntent(operation, (first, second))

    # Generic fallback: looser matches kept for backward compatibility.
    for operation, pattern in PATTERNS:
        m = re.search(pattern, text)
        if m:
            return ParsedIntent(operation, (float(m.group(1)), float(m.group(2))))

    return None


_NL_RULES: list[tuple[str, str, str]] = [
    # --- Keyword-first, explicit verb ---
    ("add", rf"\badd\s+{NUMBER}\s+(?:and|to)\s+{NUMBER}", "ab"),
    ("subtract", rf"\bsubtract\s+{NUMBER}\s+from\s+{NUMBER}", "ba"),
    ("subtract", rf"\btake\s+{NUMBER}\s+away\s+from\s+{NUMBER}", "ba"),
    ("multiply", rf"\bmultiply\s+{NUMBER}\s+(?:by|and)\s+{NUMBER}", "ab"),
    ("divide", rf"\bdivide\s+{NUMBER}\s+(?:by|into)\s+{NUMBER}", "ab"),

    # --- Number-first, spoken/word-operator phrasing ---
    # e.g. "45 plus 55", "100 minus 27", "6 times 8", "12 multiplied by 8",
    # "100 divided by 4", "40 divide 2", "40 divide by 2".
    ("add", rf"{NUMBER}\s+plus\s+{NUMBER}", "ab"),
    ("subtract", rf"{NUMBER}\s+minus\s+{NUMBER}", "ab"),
    ("subtract", rf"{NUMBER}\s+less\s+{NUMBER}", "ab"),
    ("multiply", rf"{NUMBER}\s+times\s+{NUMBER}", "ab"),
    ("multiply", rf"{NUMBER}\s+multiplied\s+by\s+{NUMBER}", "ab"),
    ("divide", rf"{NUMBER}\s+divided\s+by\s+{NUMBER}", "ab"),
    ("divide", rf"{NUMBER}\s+divide\s+by\s+{NUMBER}", "ab"),
    ("divide", rf"{NUMBER}\s+divide\s+{NUMBER}", "ab"),

    # --- "of" / "between" idioms ---
    ("add", rf"\bsum\s+of\s+{NUMBER}\s+and\s+{NUMBER}", "ab"),
    ("subtract", rf"\bdifference\s+between\s+{NUMBER}\s+and\s+{NUMBER}", "ab"),
    ("multiply", rf"\bproduct\s+of\s+{NUMBER}\s+and\s+{NUMBER}", "ab"),
    ("divide", rf"\bquotient\s+of\s+{NUMBER}\s+and\s+{NUMBER}", "ab"),

    # --- "what is / calculate X <op-word> Y" wrapper ---
    ("add", rf"\b(?:what is|calculate)\s+{NUMBER}\s+plus\s+{NUMBER}", "ab"),
    ("subtract", rf"\b(?:what is|calculate)\s+{NUMBER}\s+minus\s+{NUMBER}", "ab"),
    ("multiply", rf"\b(?:what is|calculate)\s+{NUMBER}\s+times\s+{NUMBER}", "ab"),
    ("multiply", rf"\b(?:what is|calculate)\s+{NUMBER}\s+multiplied by\s+{NUMBER}", "ab"),
    ("divide", rf"\b(?:what is|calculate)\s+{NUMBER}\s+divided by\s+{NUMBER}", "ab"),
]


PATTERNS = [
    ("add", rf"\b(?:add|plus|sum|addition)\b.*?{NUMBER}.*?(?:and|to|with)\s*{NUMBER}"),
    ("subtract", rf"\bsubtract\b\s*{NUMBER}\s*(?:from)\s*{NUMBER}"),
    ("subtract", rf"\b(?:minus|subtract)\b.*?{NUMBER}.*?(?:from|and)\s*{NUMBER}"),
    ("multiply", rf"\b(?:multiply|times|multiplied by|product)\b.*?{NUMBER}.*?(?:by|and|times)\s*{NUMBER}"),
    ("divide", rf"\b(?:divide|divided by|quotient)\b.*?{NUMBER}.*?(?:by|into)\s*{NUMBER}"),
]
