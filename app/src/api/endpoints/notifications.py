from fastapi import APIRouter

router = APIRouter()


@router.get("")
def notifications_health():
    return {"status": "notifications module ready"}
