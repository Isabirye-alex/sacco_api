"""Module for app.src.services.accounting_service."""

from typing import Any, Dict


class AccountingService:
    """Service layer for accounting and reporting concerns."""

    def get_dashboard_summary(self) -> Dict[str, Any]:
        return {
            "total_accounts": 0,
            "total_transactions": 0,
            "pending_reconciliations": 0,
        }
