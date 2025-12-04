"""
Number-to-English conversion utilities.

This module provides functions to convert numbers (integers and decimals)
to their English word representation.

Complexity Analysis:
    Time:  O(log n + d) where n is the integer part, d is decimal digits
    Space: O(log n + d) for the result string chunks
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Union

# Single digits for decimal places (includes "zero")
DIGITS: tuple[str, ...] = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)

# Word lists for number construction — O(1) lookup via direct indexing
# Note: ONES[0] is empty because zero is handled specially in integer context
ONES: tuple[str, ...] = (
    "",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)

TENS: tuple[str, ...] = (
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)

# Scale words for large numbers (each represents 10^(3*index))
THOUSANDS: tuple[str, ...] = (
    "",
    "thousand",
    "million",
    "billion",
    "trillion",
    "quadrillion",
    "quintillion",
    "sextillion",
    "septillion",
    "octillion",
    "nonillion",
    "decillion",
)

MAX_SUPPORTED_MAGNITUDE: int = len(THOUSANDS) - 1

# Type alias for acceptable numeric inputs
NumericInput = Union[int, float, str, Decimal]


def _convert_three_digits(n: int) -> str:
    """
    Convert a number less than 1000 to English.

    Time Complexity: O(1) — bounded input, constant operations
    Space Complexity: O(1) — at most 3 string parts

    Args:
        n: Integer in range [0, 999].

    Returns:
        English representation of the number.
    """
    if n == 0:
        return ""

    parts: list[str] = []

    hundreds, remainder = divmod(n, 100)
    if hundreds:
        parts.append(f"{ONES[hundreds]} hundred")

    if remainder >= 20:
        tens, ones = divmod(remainder, 10)
        parts.append(TENS[tens])
        if ones:
            parts.append(ONES[ones])
    elif remainder > 0:
        parts.append(ONES[remainder])

    return " ".join(parts)


def _integer_to_english(number: int) -> str:
    """
    Convert a non-negative integer to English words.

    Time Complexity: O(log n)
    Space Complexity: O(log n)

    Args:
        number: Non-negative integer to convert.

    Returns:
        English word representation.

    Raises:
        ValueError: If magnitude exceeds supported range.
    """
    if number == 0:
        return "zero"

    parts: list[str] = []
    magnitude = 0

    while number > 0:
        number, chunk = divmod(number, 1000)

        if chunk > 0:
            if magnitude > MAX_SUPPORTED_MAGNITUDE:
                raise ValueError(
                    f"Number too large: magnitude {magnitude} not supported"
                )

            chunk_str = _convert_three_digits(chunk)
            if magnitude > 0:
                chunk_str = f"{chunk_str} {THOUSANDS[magnitude]}"

            parts.append(chunk_str)

        magnitude += 1

    parts.reverse()
    return " ".join(parts)


def _decimal_digits_to_english(decimal_str: str) -> str:
    """
    Convert decimal digit string to English words.

    Each digit is spoken individually: "579" → "five seven nine"

    Time Complexity: O(d) where d is number of decimal digits
    Space Complexity: O(d)

    Args:
        decimal_str: String of decimal digits (e.g., "579").

    Returns:
        Space-separated digit words.
    """
    # Direct lookup for each digit — O(1) per digit, O(d) total
    return " ".join(DIGITS[int(digit)] for digit in decimal_str)


def number_to_english(number: NumericInput) -> str:
    """
    Convert a number to its English word representation.

    Supports:
    - Integers: 42 → "forty two"
    - Decimals: 3.14 → "three point one four"
    - Negative numbers: -5 → "negative five"
    - String input: "123.456" → "one hundred twenty three point four five six"

    Algorithm:
        1. Parse input to Decimal for precision (avoids float errors)
        2. Handle sign (negative prefix)
        3. Split into integer and fractional parts
        4. Convert integer part using chunked algorithm
        5. Convert fractional part digit-by-digit

    Time Complexity: O(log n + d)
        - Integer part: O(log n) where n is the integer value
        - Decimal part: O(d) where d is number of decimal digits

    Space Complexity: O(log n + d)

    Args:
        number: The number to convert (int, float, str, or Decimal).

    Returns:
        English word representation of the number.

    Raises:
        ValueError: If input is invalid or magnitude exceeds decillions.

    Examples:
        >>> number_to_english(0)
        'zero'
        >>> number_to_english(42)
        'forty two'
        >>> number_to_english(-5)
        'negative five'
        >>> number_to_english(3.14159)
        'three point one four one five nine'
        >>> number_to_english("10300000067.579")
        'ten billion three hundred million sixty seven point five seven nine'
    """
    # Convert to Decimal for precision — avoids float representation errors
    # e.g., float 0.1 + 0.2 != 0.3, but Decimal handles this correctly
    try:
        dec = Decimal(str(number))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid number: {number}") from exc

    # Handle negative numbers
    is_negative = dec < 0
    if is_negative:
        dec = -dec

    # Split into integer and fractional parts using Decimal's as_tuple()
    # This is more efficient than string splitting for edge cases
    sign, digits, exponent = dec.as_tuple()

    if exponent >= 0:
        # Pure integer (no decimal point)
        integer_value = int(dec)
        result = _integer_to_english(integer_value)
    else:
        # Has decimal component
        # exponent is negative, indicates decimal places
        decimal_places = -exponent
        total_digits = len(digits)

        # Separate integer digits from fractional digits
        if total_digits <= decimal_places:
            # Number like 0.123 — pad with leading zeros
            integer_value = 0
            fractional_str = "0" * (decimal_places - total_digits) + "".join(
                str(d) for d in digits
            )
        else:
            # Number like 123.456
            split_point = total_digits - decimal_places
            integer_digits = digits[:split_point]
            fractional_digits = digits[split_point:]

            integer_value = int("".join(str(d) for d in integer_digits))
            fractional_str = "".join(str(d) for d in fractional_digits)

        # Check if fractional part is all zeros (e.g., 1.0, 1e6 as float)
        # If so, treat as whole number for cleaner output
        if all(c == "0" for c in fractional_str):
            result = _integer_to_english(integer_value)
        else:
            # Build result with decimal part
            integer_part = _integer_to_english(integer_value)
            fractional_part = _decimal_digits_to_english(fractional_str)
            result = f"{integer_part} point {fractional_part}"

    # Add negative prefix if needed
    if is_negative:
        result = f"negative {result}"

    return result
