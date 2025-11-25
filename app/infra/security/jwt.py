from datetime import timedelta, datetime
from jose import jwt
from app.core.config.settings import settings


def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=60)
    data.update({"exp": expire})
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
