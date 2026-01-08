import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

ENV_LOGIN = os.getenv("ENV_LOGIN", "ndevelopment")

if ENV_LOGIN == "production":
    DATABASE_URL = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or os.getenv("POSTGRES_URL")
    )

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no está configurada en producción")

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql://", 1
        )
else:
    DATABASE_URL = "sqlite+aiosqlite:///./app.db"
