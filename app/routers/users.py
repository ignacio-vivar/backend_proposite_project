from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.models.user import User, USER_TYPE, UserUpdate
from app.schemas.user import UserCreate, UserResponse
from app.routers.auth import check_admin
from sqlalchemy import select

router = APIRouter()

admin_router = APIRouter(prefix="/admin", tags=["Admin - Users"], dependencies=[Depends(check_admin)])

@admin_router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar email duplicado
    if user_update.email and user_update.email != db_user.email:
        result = await db.execute(
            select(User).where(
                User.email == user_update.email,
                User.id != user_id
            )
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field in ["email", "name"]:
            setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)

    return {"message": "User updated successfully"}

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    db_user = result.scalars().first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already exist")

    new_user = User(
        email=user.email,
        name=user.name,
        user_type_id=USER_TYPE["Student"]
    )
    new_user.set_password(user.password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


