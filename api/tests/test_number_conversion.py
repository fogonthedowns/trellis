"""
Unit tests for the number-to-English conversion logic.

These tests focus on the pure conversion function, isolated
from the HTTP layer. Uses SimpleTestCase since no database
access is required.
"""
from decimal import Decimal

from django.test import SimpleTestCase

from api.utils import number_to_english


class NumberToEnglishBasicTests(SimpleTestCase):
    """Test basic number conversions."""

    def test_zero_returns_zero(self):
        """Zero should return 'zero'."""
        self.assertEqual(number_to_english(0), "zero")

    def test_single_digits(self):
        """Single digit numbers should return correct word."""
        cases = [
            (1, "one"),
            (2, "two"),
            (3, "three"),
            (4, "four"),
            (5, "five"),
            (6, "six"),
            (7, "seven"),
            (8, "eight"),
            (9, "nine"),
        ]
        for number, expected in cases:
            with self.subTest(number=number):
                self.assertEqual(number_to_english(number), expected)


class NumberToEnglishTeensTests(SimpleTestCase):
    """Test teen number conversions (10-19)."""

    def test_teens(self):
        """Teen numbers should return correct word."""
        cases = [
            (10, "ten"),
            (11, "eleven"),
            (12, "twelve"),
            (13, "thirteen"),
            (14, "fourteen"),
            (15, "fifteen"),
            (16, "sixteen"),
            (17, "seventeen"),
            (18, "eighteen"),
            (19, "nineteen"),
        ]
        for number, expected in cases:
            with self.subTest(number=number):
                self.assertEqual(number_to_english(number), expected)


class NumberToEnglishTensTests(SimpleTestCase):
    """Test tens conversions (20-99)."""

    def test_round_tens(self):
        """Round tens should return correct word."""
        cases = [
            (20, "twenty"),
            (30, "thirty"),
            (40, "forty"),
            (50, "fifty"),
            (60, "sixty"),
            (70, "seventy"),
            (80, "eighty"),
            (90, "ninety"),
        ]
        for number, expected in cases:
            with self.subTest(number=number):
                self.assertEqual(number_to_english(number), expected)

    def test_compound_tens(self):
        """Compound tens should return correct words."""
        self.assertEqual(number_to_english(21), "twenty one")
        self.assertEqual(number_to_english(42), "forty two")
        self.assertEqual(number_to_english(99), "ninety nine")


class NumberToEnglishHundredsTests(SimpleTestCase):
    """Test hundreds conversions (100-999)."""

    def test_round_hundreds(self):
        """Round hundreds should return correct word."""
        self.assertEqual(number_to_english(100), "one hundred")
        self.assertEqual(number_to_english(500), "five hundred")
        self.assertEqual(number_to_english(900), "nine hundred")

    def test_hundreds_with_ones(self):
        """Hundreds with ones should return correct words."""
        self.assertEqual(number_to_english(105), "one hundred five")
        self.assertEqual(number_to_english(309), "three hundred nine")

    def test_hundreds_with_tens(self):
        """Hundreds with tens should return correct words."""
        self.assertEqual(number_to_english(110), "one hundred ten")
        self.assertEqual(number_to_english(215), "two hundred fifteen")

    def test_hundreds_with_compound(self):
        """Hundreds with compound tens should return correct words."""
        self.assertEqual(number_to_english(123), "one hundred twenty three")
        self.assertEqual(number_to_english(999), "nine hundred ninety nine")


class NumberToEnglishLargeNumbersTests(SimpleTestCase):
    """Test large number conversions (1000+)."""

    def test_thousands(self):
        """Thousands should return correct words."""
        self.assertEqual(number_to_english(1000), "one thousand")
        self.assertEqual(
            number_to_english(1234),
            "one thousand two hundred thirty four",
        )
        self.assertEqual(number_to_english(10000), "ten thousand")
        self.assertEqual(number_to_english(100000), "one hundred thousand")

    def test_millions(self):
        """Millions should return correct words."""
        self.assertEqual(number_to_english(1000000), "one million")
        self.assertEqual(
            number_to_english(12345678),
            "twelve million three hundred forty five thousand six hundred seventy eight",
        )

    def test_billions(self):
        """Billions should return correct words."""
        self.assertEqual(number_to_english(1000000000), "one billion")

    def test_trillions(self):
        """Trillions should return correct words."""
        self.assertEqual(number_to_english(10**12), "one trillion")


class NumberToEnglishNegativeTests(SimpleTestCase):
    """Test negative number conversions."""

    def test_negative_single_digit(self):
        """Negative single digit should have 'negative' prefix."""
        self.assertEqual(number_to_english(-5), "negative five")

    def test_negative_large_number(self):
        """Negative large number should have 'negative' prefix."""
        self.assertEqual(number_to_english(-1000), "negative one thousand")

    def test_negative_decimal(self):
        """Negative decimal should have 'negative' prefix."""
        self.assertEqual(
            number_to_english(-3.14),
            "negative three point one four",
        )


class NumberToEnglishDecimalTests(SimpleTestCase):
    """Test decimal number conversions."""

    def test_simple_decimal(self):
        """Simple decimal should return correct words."""
        self.assertEqual(
            number_to_english(3.14),
            "three point one four",
        )

    def test_decimal_with_zero_integer(self):
        """Decimal less than 1 should return 'zero point ...'."""
        self.assertEqual(
            number_to_english(0.5),
            "zero point five",
        )
        self.assertEqual(
            number_to_english(0.123),
            "zero point one two three",
        )

    def test_decimal_with_leading_zeros(self):
        """Decimal with leading zeros in fractional part."""
        self.assertEqual(
            number_to_english(1.01),
            "one point zero one",
        )
        self.assertEqual(
            number_to_english(5.007),
            "five point zero zero seven",
        )

    def test_decimal_with_trailing_zeros(self):
        """Decimal with trailing zeros (from string input)."""
        self.assertEqual(
            number_to_english("1.50"),
            "one point five zero",
        )
        self.assertEqual(
            number_to_english("3.100"),
            "three point one zero zero",
        )

    def test_long_decimal(self):
        """Long decimal should process all digits."""
        self.assertEqual(
            number_to_english(3.14159265),
            "three point one four one five nine two six five",
        )

    def test_large_number_with_decimal(self):
        """Large number with decimal part."""
        self.assertEqual(
            number_to_english(10300000067.579),
            "ten billion three hundred million sixty seven point five seven nine",
        )

    def test_string_input_decimal(self):
        """String input with decimal should work."""
        self.assertEqual(
            number_to_english("123.456"),
            "one hundred twenty three point four five six",
        )

    def test_decimal_type_input(self):
        """Decimal type input should work."""
        self.assertEqual(
            number_to_english(Decimal("99.99")),
            "ninety nine point nine nine",
        )

    def test_scientific_notation(self):
        """Scientific notation should be handled."""
        # Float 1e6 becomes 1000000.0, trailing zeros stripped → "one million"
        self.assertEqual(
            number_to_english(1e6),
            "one million",
        )
        # String scientific notation
        self.assertEqual(
            number_to_english("1e6"),
            "one million",
        )
        # Scientific with decimal — resolves to whole number
        self.assertEqual(
            number_to_english("1.5e2"),
            "one hundred fifty",
        )


class NumberToEnglishEdgeCasesTests(SimpleTestCase):
    """Test edge cases and error conditions."""

    def test_number_with_internal_zeros(self):
        """Numbers with internal zeros should be handled correctly."""
        self.assertEqual(number_to_english(101), "one hundred one")
        self.assertEqual(number_to_english(1001), "one thousand one")
        self.assertEqual(
            number_to_english(1000001),
            "one million one",
        )

    def test_max_supported_number(self):
        """Maximum supported magnitude should work."""
        self.assertEqual(number_to_english(10**12), "one trillion")

    def test_number_exceeding_max_magnitude_raises_error(self):
        """Number exceeding maximum magnitude should raise ValueError."""
        too_large = 10**36

        with self.assertRaises(ValueError) as context:
            number_to_english(too_large)

        self.assertIn("Number too large", str(context.exception))

    def test_invalid_input_raises_error(self):
        """Invalid input should raise ValueError."""
        with self.assertRaises(ValueError):
            number_to_english("not a number")

        with self.assertRaises(ValueError):
            number_to_english("abc123")

    def test_integer_from_string(self):
        """Integer provided as string should work."""
        self.assertEqual(number_to_english("42"), "forty two")
        self.assertEqual(number_to_english("1000"), "one thousand")

    def test_very_small_decimal(self):
        """Very small decimals should work."""
        self.assertEqual(
            number_to_english(0.001),
            "zero point zero zero one",
        )

    def test_whole_number_as_decimal(self):
        """Whole number with .0 should not show 'point' (trailing zeros stripped)."""
        self.assertEqual(number_to_english(5), "five")
        # String "5.0" — trailing zeros stripped for cleaner output
        self.assertEqual(number_to_english("5.0"), "five")
        self.assertEqual(number_to_english(5.0), "five")
        self.assertEqual(number_to_english("100.00"), "one hundred")
