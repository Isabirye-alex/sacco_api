"""Reporting endpoints used to confirm that report-related routes are available."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def reports_health():
    """
    Confirm that the reports API module is reachable.

    This lightweight endpoint helps verify that the reporting routes are mounted
    correctly and that the application can respond to report-related probes. It
    does not generate any report data on its own.

    Returns:
        A simple payload indicating that the reports module is available.
    """
    return {"status": "reports module ready"}
