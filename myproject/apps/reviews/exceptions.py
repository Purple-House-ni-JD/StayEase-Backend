from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default handler to return a consistent JSON shape for
    duplicate-review validation errors.
    """
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError) and isinstance(exc.detail, dict):
        booking_errors = exc.detail.get("booking", [])
        if any("already submitted a review" in str(e) for e in booking_errors):
            return Response(
                {
                    "error": "You have already submitted a review for this booking.",
                    "error_code": "DUPLICATE_REVIEW",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    return response