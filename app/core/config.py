import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Detectar ambiente
ENV_LOGIN = os.getenv("ENV_LOGIN", "development")

# Usar PostgreSQL en producción, SQLite en desarrollo
if ENV_LOGIN == "production":
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Vercel usa postgres:// pero SQLAlchemy necesita postgresql://
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = "sqlite:///./app.db"
