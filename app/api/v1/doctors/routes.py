from fastapi import APIRouter

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/health")
async def health_check():
    return {"status": "doctors router OK"}
