"""Health-check endpoints used to verify API availability."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check():
    """
    Return a simple readiness signal for the API service.

    This endpoint is intended for uptime probes, container health checks, and
    quick verification that the application is responding correctly. The response
    is intentionally lightweight and does not require any authentication.

    Returns:
        A JSON object indicating that the service is available.
    """
    return {"status": "ok"}
