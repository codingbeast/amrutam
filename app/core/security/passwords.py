from passlib.context import CryptContext

# Use Argon2 as the only hashing algorithm
pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash a plain password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored Argon2 hash."""
    return pwd_context.verify(plain_password, hashed_password)
