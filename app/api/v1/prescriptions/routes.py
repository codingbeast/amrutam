from fastapi import APIRouter

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.get("/health")
async def health_check():
    return {"status": "prescriptions router OK"}
