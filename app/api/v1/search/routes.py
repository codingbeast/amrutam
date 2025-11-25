from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/health")
async def health_check():
    return {"status": "search router OK"}
