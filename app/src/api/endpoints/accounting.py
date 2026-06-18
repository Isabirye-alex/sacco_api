from fastapi import APIRouter, Depends
from app.src.services.accounting_service import AccountingService

router = APIRouter()


def get_accounting_service() -> AccountingService:
    return AccountingService()


@router.get("/dashboard-summary")
def dashboard_summary(
    service: AccountingService = Depends(get_accounting_service),
):
    return service.get_dashboard_summary()
