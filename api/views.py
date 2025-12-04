"""
API views for number-to-English conversion.

This module provides a RESTful endpoint to convert integers
to their English word representation.
"""
import logging
from functools import lru_cache

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .constants import STATUS_OK, STATUS_ERROR
from .serializers import NumberConversionSerializer, NumberConversionResponseSerializer
from .utils import number_to_english

logger = logging.getLogger(__name__)


# Cache the conversion results.
# In a real distributed system, use Redis or Memcached.
# maxsize=1024 is arbitrary but prevents unbounded memory growth.
@lru_cache(maxsize=1024)
def cached_number_to_english(number: int) -> str:
    """Cached wrapper around number_to_english for efficiency."""
    return number_to_english(number)


class NumberToEnglishView(APIView):
    """
    Convert a number to its English word representation.

    Accepts both GET (with query param) and POST (with JSON body).
    """

    @extend_schema(
        summary="Convert number to English (GET)",
        description="Convert an integer to its English word representation using query parameters.",
        parameters=[NumberConversionSerializer],
        responses={
            200: OpenApiResponse(
                response=NumberConversionResponseSerializer,
                description="Successful conversion",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"status": "ok", "num_in_english": "one hundred twenty three"},
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Invalid input",
                examples=[
                    OpenApiExample(
                        "Missing number",
                        value={"status": "error", "message": {"number": ["This field is required."]}},
                    ),
                    OpenApiExample(
                        "Number too large",
                        value={"status": "error", "message": "Number too large: magnitude 12 not supported"},
                    ),
                ],
            ),
        },
        tags=["Number Conversion"],
    )
    def get(self, request: Request) -> Response:
        """Handle GET requests with number as query parameter."""
        return self._convert_number(request.query_params)

    @extend_schema(
        summary="Convert number to English (POST)",
        description="Convert an integer to its English word representation using JSON body.",
        request=NumberConversionSerializer,
        responses={
            200: OpenApiResponse(
                response=NumberConversionResponseSerializer,
                description="Successful conversion",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"status": "ok", "num_in_english": "twelve million three hundred forty five thousand six hundred seventy eight"},
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Invalid input",
                examples=[
                    OpenApiExample(
                        "Invalid format",
                        value={"status": "error", "message": {"number": ["A valid integer is required."]}},
                    ),
                ],
            ),
        },
        tags=["Number Conversion"],
    )
    def post(self, request: Request) -> Response:
        """Handle POST requests with number in request body."""
        return self._convert_number(request.data)

    def _convert_number(self, data: dict) -> Response:
        """
        Core conversion logic shared between GET and POST.

        Args:
            data: Dictionary containing 'number' key.

        Returns:
            Response with English representation or error message.
        """
        serializer = NumberConversionSerializer(data=data)

        if not serializer.is_valid():
            logger.warning("Invalid input received: %s", serializer.errors)
            return Response(
                {"status": STATUS_ERROR, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        number = serializer.validated_data["number"]

        try:
            english_text = cached_number_to_english(number)
            logger.debug("Converted %d to '%s'", number, english_text)
            return Response({"status": STATUS_OK, "num_in_english": english_text})

        except ValueError as exc:
            logger.warning("Number too large: %d - %s", number, exc)
            return Response(
                {"status": STATUS_ERROR, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            logger.exception("Unexpected error converting %d: %s", number, exc)
            return Response(
                {"status": STATUS_ERROR, "message": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
