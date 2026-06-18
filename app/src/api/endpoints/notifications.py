"""Notification module endpoints for health and routing verification."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def notifications_health():
    """
    Verify that the notifications API module is reachable.

    This endpoint is primarily used for basic service checks and to confirm that
    the notification route group has been registered correctly. It does not send
    messages or perform any downstream processing.

    Returns:
        A simple payload indicating that the notifications endpoint is available.
    """
    return {"status": "notifications module ready"}
