from fastapi import APIRouter

router = APIRouter(prefix="/consultations", tags=["consultations"])

@router.get("/health")
async def health_check():
    return {"status": "consultations router OK"}
