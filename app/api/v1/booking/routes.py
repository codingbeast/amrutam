from fastapi import APIRouter

router = APIRouter(prefix="/booking", tags=["booking"])

@router.get("/health")
async def health_check():
    return {"status": "booking router OK"}
