from fastapi import APIRouter
from app.src.api.endpoints.users import router as users_route
from app.src.api.endpoints.auth import router as auth_route
from app.src.api.endpoints.logs import router as logs_route
from app.src.api.endpoints.tenant_endpoint.tenant_endpoint import router as org_router
from app.src.api.endpoints.member import router as member_route
from app.src.api.endpoints.savings import router as savings_route
from app.src.api.endpoints.shares import router as shares_route
from app.src.api.endpoints.ledger import router as ledger_route
from app.src.api.endpoints.loans import router as loans_route
from app.src.api.endpoints.loans_extended import router as loans_extended_route
from app.src.api.endpoints.shares_extended import router as shares_extended_route
from app.src.api.endpoints.mobile_money import router as mobile_money_route
from app.src.api.endpoints.accounting import router as accounting_route
from app.src.api.endpoints.notifications import router as notifications_route
from app.src.api.endpoints.reports import router as reports_route
from app.src.api.endpoints.admin import router as admin_route
from app.src.api.endpoints.health import router as health_route

# Domain-specific routers are grouped here to keep the API layout consistent with
# the proposal's modular architecture.

api_router = APIRouter()

api_router.include_router(users_route, prefix="/users", tags=["users"])
api_router.include_router(auth_route, prefix="/auth", tags=["auth"])
api_router.include_router(logs_route, prefix="/login-logs", tags=["login-logs"])
api_router.include_router(org_router, prefix="/organisation", tags=["organisation"])
api_router.include_router(member_route, prefix="/members", tags=["members"])
api_router.include_router(savings_route, prefix="/savings", tags=["savings"])
api_router.include_router(shares_route, prefix="/shares", tags=["shares"])
api_router.include_router(
    shares_extended_route, prefix="/shares-extended", tags=["shares"]
)
api_router.include_router(ledger_route, prefix="/ledger", tags=["ledger"])
api_router.include_router(loans_route, prefix="/loans", tags=["loans"])
api_router.include_router(
    loans_extended_route, prefix="/loans-extended", tags=["loans"]
)
api_router.include_router(
    mobile_money_route, prefix="/mobile-money", tags=["mobile-money"]
)
api_router.include_router(
    accounting_route, prefix="/accounting", tags=["accounting"]
)
api_router.include_router(
    notifications_route, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(reports_route, prefix="/reports", tags=["reports"])
api_router.include_router(admin_route, prefix="/admin", tags=["admin"])
api_router.include_router(health_route, prefix="/health", tags=["health"])

