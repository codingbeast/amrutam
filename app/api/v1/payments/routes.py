from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/health")
async def health_check():
    return {"status": "payments router OK"}
