from fastapi import APIRouter

router = APIRouter(prefix="/availability", tags=["availability"])

@router.get("/health")
async def health_check():
    return {"status": "availability router OK"}
