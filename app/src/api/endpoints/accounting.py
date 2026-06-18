"""Accounting endpoints that expose business summaries for dashboards and finance views."""

from fastapi import APIRouter, Depends
from app.src.services.accounting_service import AccountingService

router = APIRouter()


def get_accounting_service() -> AccountingService:
    """Build a fresh accounting service instance for each request."""
    return AccountingService()


@router.get("/dashboard-summary")
def dashboard_summary(
    service: AccountingService = Depends(get_accounting_service),
):
    """
    Fetch a high-level accounting summary for reporting dashboards.

    This endpoint aggregates key financial indicators that are typically used by
    finance and admin users to monitor overall performance. The response shape is
    intentionally summary-based and should be used for dashboard widgets rather
    than detailed ledger inspection.

    Returns:
        A dictionary containing aggregated accounting metrics.
    """
    return service.get_dashboard_summary()
