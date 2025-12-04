"""
Integration tests for the number conversion API views.

Uses DRF's APITestCase for proper API testing with
correct content types and response handling.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.constants import STATUS_ERROR, STATUS_OK


class NumberToEnglishViewTests(APITestCase):
    """Test cases for the NumberToEnglishView endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        # Use exact assignment URL (without trailing slash)
        self.url = "/num_to_english"

    # ==================== Integer Tests ====================

    def test_get_valid_integer_returns_english_representation(self):
        """GET with valid integer returns correct English representation."""
        response = self.client.get(self.url, {"number": "12345678"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], STATUS_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "twelve million three hundred forty five thousand six hundred seventy eight",
        )

    def test_post_valid_integer_returns_english_representation(self):
        """POST with valid integer returns correct English representation."""
        response = self.client.post(
            self.url, {"number": 12345678}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], STATUS_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "twelve million three hundred forty five thousand six hundred seventy eight",
        )

    def test_get_zero_returns_zero(self):
        """GET with zero returns 'zero'."""
        response = self.client.get(self.url, {"number": "0"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num_in_english"], "zero")

    def test_get_negative_integer_returns_negative_prefix(self):
        """GET with negative integer returns 'negative' prefix."""
        response = self.client.get(self.url, {"number": "-42"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num_in_english"], "negative forty two")

    # ==================== Decimal Tests ====================

    def test_get_simple_decimal_returns_english(self):
        """GET with simple decimal returns correct representation."""
        response = self.client.get(self.url, {"number": "3.14"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], STATUS_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "three point one four",
        )

    def test_post_decimal_returns_english(self):
        """POST with decimal returns correct representation."""
        response = self.client.post(
            self.url, {"number": 3.14159}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "three point one four one five nine",
        )

    def test_get_decimal_less_than_one(self):
        """GET with decimal < 1 returns 'zero point ...'."""
        response = self.client.get(self.url, {"number": "0.579"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "zero point five seven nine",
        )

    def test_get_decimal_with_leading_zeros(self):
        """GET with decimal having leading zeros in fractional part."""
        response = self.client.get(self.url, {"number": "1.007"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "one point zero zero seven",
        )

    def test_get_large_number_with_decimal(self):
        """GET with large number and decimal returns correct representation."""
        response = self.client.get(self.url, {"number": "10300000067.579"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "ten billion three hundred million sixty seven point five seven nine",
        )

    def test_get_negative_decimal(self):
        """GET with negative decimal returns correct representation."""
        response = self.client.get(self.url, {"number": "-99.99"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "negative ninety nine point nine nine",
        )

    # ==================== Error Cases ====================

    def test_get_missing_number_returns_400(self):
        """GET without number parameter returns 400 error."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], STATUS_ERROR)
        self.assertIn("number", response.data["message"])

    def test_post_missing_number_returns_400(self):
        """POST without number in body returns 400 error."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], STATUS_ERROR)
        self.assertIn("number", response.data["message"])

    def test_get_invalid_number_format_returns_400(self):
        """GET with non-numeric value returns 400 error."""
        response = self.client.get(self.url, {"number": "abc"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], STATUS_ERROR)
        self.assertIn("number", response.data["message"])

    def test_get_number_too_large_returns_400(self):
        """GET with extremely large number returns 400 error."""
        huge_number = "1" + "0" * 100
        response = self.client.get(self.url, {"number": huge_number})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], STATUS_ERROR)
        # Serializer catches numbers exceeding max_digits (50)
        self.assertIn("number", response.data["message"])

    def test_post_string_number_is_accepted(self):
        """POST with string number is properly converted."""
        response = self.client.post(
            self.url, {"number": "999.99"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["num_in_english"],
            "nine hundred ninety nine point nine nine",
        )

    def test_empty_string_returns_400(self):
        """Empty string for number returns 400 error."""
        response = self.client.get(self.url, {"number": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_scientific_notation_accepted(self):
        """Scientific notation is accepted and converted."""
        response = self.client.get(self.url, {"number": "1e6"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["num_in_english"], "one million")
