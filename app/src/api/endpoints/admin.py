"""Administrative health endpoints for verifying the admin API surface."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def admin_health():
    """
    Confirm that the admin API module is reachable.

    This lightweight endpoint is useful for startup checks and for verifying that
    the admin routing configuration is loaded correctly. It does not perform any
    authentication or business validation.

    Returns:
        A simple status payload indicating that the admin module is available.
    """
    return {"status": "admin module ready"}
