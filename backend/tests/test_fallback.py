from app.fallback.parser import looks_like_multiple_calculations, parse_intent


def test_add():
    parsed = parse_intent("Add 3 and 4")
    assert parsed.operation == "add"
    assert parsed.operands == (3.0, 4.0)


def test_subtract():
    parsed = parse_intent("Subtract 18 from 50")
    assert parsed.operation == "subtract"
    assert parsed.operands == (50.0, 18.0)


def test_multiply():
    parsed = parse_intent("Multiply 5 by 6")
    assert parsed.operation == "multiply"
    assert parsed.operands == (5.0, 6.0)


def test_divide():
    parsed = parse_intent("Divide 144 by 12")
    assert parsed.operation == "divide"
    assert parsed.operands == (144.0, 12.0)


def test_unsupported():
    assert parse_intent("What's the weather today?") is None


# --- Regression tests for the fallback-parser bug ---
# Previously the fallback parser had NO support for plain symbolic
# expressions, so "2 + 5" only worked when Gemini itself was reachable.
# When Gemini was rate-limited/timed-out, the exact same input silently
# fell through to the generic "unsupported" message.

def test_symbolic_add():
    parsed = parse_intent("2 + 5")
    assert parsed.operation == "add"
    assert parsed.operands == (2.0, 5.0)


def test_symbolic_subtract_no_spaces():
    parsed = parse_intent("100-27")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 27.0)


def test_symbolic_subtract_extra_spaces():
    parsed = parse_intent("100   -   27")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 27.0)


def test_symbolic_negative_numbers():
    parsed = parse_intent("-10 + -20")
    assert parsed.operation == "add"
    assert parsed.operands == (-10.0, -20.0)


def test_symbolic_decimals():
    parsed = parse_intent("100.25 + 50.75")
    assert parsed.operation == "add"
    assert parsed.operands == (100.25, 50.75)


def test_symbolic_multiply():
    parsed = parse_intent("6 * 8")
    assert parsed.operation == "multiply"
    assert parsed.operands == (6.0, 8.0)


def test_symbolic_divide():
    parsed = parse_intent("40 / 2")
    assert parsed.operation == "divide"
    assert parsed.operands == (40.0, 2.0)


def test_unicode_operators():
    parsed = parse_intent("100 \u00f7 5")  # 100 ÷ 5
    assert parsed.operation == "divide"
    assert parsed.operands == (100.0, 5.0)

    parsed = parse_intent("10 \u00d7 5")  # 10 × 5
    assert parsed.operation == "multiply"
    assert parsed.operands == (10.0, 5.0)

    parsed = parse_intent("10 \u2212 5")  # 10 − 5
    assert parsed.operation == "subtract"
    assert parsed.operands == (10.0, 5.0)


# --- Regression tests for the multi-expression bug ---
# "10 + 20 10 - 5 10 * 5 100 / 5" previously reached Gemini and produced a
# garbled, partially-serialized response. It must now be rejected up front.

def test_multiple_calculations_detected():
    assert looks_like_multiple_calculations(
        "10 + 20 10 - 5 10 * 5 100 / 5"
    ) is True


def test_single_calculation_not_flagged_as_multiple():
    assert looks_like_multiple_calculations("2 + 5") is False
    assert looks_like_multiple_calculations("Add 3 and 4") is False


def test_multiple_calculations_not_parsed():
    assert parse_intent("10 + 20 10 - 5 10 * 5 100 / 5") is None


# --- Regression tests: number-first / spoken phrasing gap ---
# Found by live-testing the running server (not just unit tests): the
# fallback parser only understood "divide X by Y" (keyword first). Common
# number-first phrasing like "100 divided by 0" and bare "40 divide 2"
# silently fell through to "unsupported" whenever Gemini was unavailable.

def test_number_first_divided_by():
    parsed = parse_intent("100 divided by 0")
    assert parsed.operation == "divide"
    assert parsed.operands == (100.0, 0.0)


def test_number_first_bare_divide():
    parsed = parse_intent("40 divide 2")
    assert parsed.operation == "divide"
    assert parsed.operands == (40.0, 2.0)


def test_number_first_divide_by():
    parsed = parse_intent("40 divide by 2")
    assert parsed.operation == "divide"
    assert parsed.operands == (40.0, 2.0)


def test_number_first_plus():
    parsed = parse_intent("45 plus 55")
    assert parsed.operation == "add"
    assert parsed.operands == (45.0, 55.0)


def test_number_first_minus():
    parsed = parse_intent("100 minus 27")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 27.0)


def test_number_first_less():
    parsed = parse_intent("100 less 27")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 27.0)


def test_number_first_times():
    parsed = parse_intent("6 times 8")
    assert parsed.operation == "multiply"
    assert parsed.operands == (6.0, 8.0)


def test_number_first_multiplied_by():
    parsed = parse_intent("12 multiplied by 8")
    assert parsed.operation == "multiply"
    assert parsed.operands == (12.0, 8.0)


def test_take_away_from():
    parsed = parse_intent("take 27 away from 100")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 27.0)


def test_sum_of_idiom():
    parsed = parse_intent("What is the sum of 25 and 75?")
    assert parsed.operation == "add"
    assert parsed.operands == (25.0, 75.0)


def test_difference_between_idiom():
    parsed = parse_intent("What is the difference between 100 and 40?")
    assert parsed.operation == "subtract"
    assert parsed.operands == (100.0, 40.0)


def test_product_of_idiom():
    parsed = parse_intent("What is the product of 12 and 5?")
    assert parsed.operation == "multiply"
    assert parsed.operands == (12.0, 5.0)


def test_quotient_of_idiom():
    parsed = parse_intent("What is the quotient of 100 and 4?")
    assert parsed.operation == "divide"
    assert parsed.operands == (100.0, 4.0)


# --- Regression test: the word "zero" wasn't recognized as a number ---
# "Divide 50 by zero" is one of the exact phrasings in the user's own
# test plan and previously fell through to "unsupported".

def test_word_zero_recognized_as_number():
    parsed = parse_intent("Divide 50 by zero")
    assert parsed.operation == "divide"
    assert parsed.operands == (50.0, 0.0)


def test_word_zero_number_first_phrasing():
    parsed = parse_intent("What is 10 divided by zero?")
    assert parsed.operation == "divide"
    assert parsed.operands == (10.0, 0.0)
