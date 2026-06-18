from fastapi import APIRouter

router = APIRouter()


@router.get("")
def reports_health():
    return {"status": "reports module ready"}
