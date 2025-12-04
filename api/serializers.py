"""
Serializers for the number conversion API.

These serializers handle input validation and response schema
documentation for the API endpoints.
"""
from decimal import Decimal, InvalidOperation

from rest_framework import serializers


class FlexibleNumberField(serializers.Field):
    """
    Custom field that accepts integers, floats, or decimal strings.

    Converts input to Decimal for precision, avoiding float representation errors.
    """

    default_error_messages = {
        "invalid": "A valid number is required.",
        "max_digits": "Number has too many digits.",
    }

    def __init__(self, max_digits: int = 50, **kwargs):
        self.max_digits = max_digits
        super().__init__(**kwargs)

    def to_internal_value(self, data) -> Decimal:
        """Convert input to Decimal."""
        if data is None or data == "":
            self.fail("invalid")

        # Accept int, float, str, or Decimal
        try:
            # Convert to string first to handle floats precisely
            decimal_value = Decimal(str(data))
        except (InvalidOperation, ValueError, TypeError):
            self.fail("invalid")

        # Check digit count to prevent DoS with huge numbers
        sign, digits, exponent = decimal_value.as_tuple()
        if len(digits) > self.max_digits:
            self.fail("max_digits")

        return decimal_value

    def to_representation(self, value) -> str:
        """Convert Decimal to string for JSON serialization."""
        return str(value)


class NumberConversionSerializer(serializers.Serializer):
    """
    Serializer for number conversion input.

    Accepts integers, floats, or decimal strings.
    """

    number = FlexibleNumberField(
        required=True,
        help_text="The number to convert to English words. Accepts integers, decimals, or numeric strings.",
        max_digits=50,
    )


class NumberConversionResponseSerializer(serializers.Serializer):
    """
    Serializer for number conversion response.

    Used for API documentation schema generation.
    """

    status = serializers.CharField(
        help_text="Response status: 'ok' or 'error'.",
    )
    num_in_english = serializers.CharField(
        help_text="The English word representation of the number.",
        required=False,
    )
    message = serializers.CharField(
        help_text="Error message (only present on error).",
        required=False,
    )
