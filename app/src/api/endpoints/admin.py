from fastapi import APIRouter

router = APIRouter()


@router.get("")
def admin_health():
    return {"status": "admin module ready"}
