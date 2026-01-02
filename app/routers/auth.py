from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from app.database.database import get_db
from app.models.user import User, USER_TYPE
from app.schemas.token import Token
from app.core.config import ENV_LOGIN
from app.core.security import create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()

if ENV_LOGIN == "development":
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth", auto_error=False)
else:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

@router.post("/auth", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    is_teacher = user.user_type_id == USER_TYPE["Teacher"]
    is_admin = user.user_type_id == USER_TYPE["Admin"]
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "isTeacher": is_teacher,
            "isAdmin": is_admin
        },
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Acá me logeo solo supuestamente
    if ENV_LOGIN == "development":
        dev_user = db.query(User).filter(User.email == "admin@gmail.com").first()
        if dev_user:
            return dev_user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )
    
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not isinstance(user_id,str) or not user_id:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception
    

def check_admin(current_user: User = Depends(get_current_user)):

    is_admin = bool(current_user.user_type_id == 3)

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized Not Admin",
        )
    return current_user
