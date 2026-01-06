from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
from app.database.database import get_db
from app.models.user import User, USER_TYPE, UserUpdate
from app.schemas.user import UserCreate, UserResponse
from app.routers.auth import check_admin
from sqlalchemy import select

router = APIRouter()

admin_router = APIRouter(prefix="/admin", tags=["Admin - Users"], dependencies=[Depends(check_admin)])
router_develop = APIRouter(tags=["development"], prefix="/develop")

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

# @router.get("/me", response_model=UserResponse)
# async def get_current_user_info(current_user: User = Depends(get_current_user)):
#     """
#     Obtiene la información del usuario autenticado.
#     """
#     if not isinstance(current_user.id, int) or not isinstance(current_user.email, str) or not isinstance(current_user.name, str) :
#         return "Error de tipo con las propiedades"
#
#     return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name)
#
# @router.get("/getName", response_model=UserResponseName)
# async def get_current_user_name(current_user: User = Depends(get_current_user)):
#     """
#     Obtiene la información del usuario autenticado.
#     """
#     if not isinstance(current_user.name, str):
#         return "Error la propiedad name no es de tipo string"
#
#     return UserResponseName(name=current_user.name)
#
# # Only for development
# @router_develop.get("/getAll", response_model=List[UserResponse],
#             summary="Obtener todos los usuarios",
#             description="Devuelve una lista de todos los usuarios registrados.")
# async def get_all_users(db: AsyncSession = Depends(get_db)):
#
#     result = await db.execute(select(User))
#     users = result.scalars().all()
#
#     return users
#
# @router_develop.get("/get/{user_id}", response_model=UserResponse)
# async def get_user(
#     user_id: int,
#     db: AsyncSession = Depends(get_db),
# ):
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalars().first()
#
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#
#     if not isinstance(user.id, int) or not isinstance(user.email, str) or not isinstance(user.name, str) :
#         return "Error de tipo con las propiedades"
#
#     return UserResponse(id=user.id, email=user.email, name=user.name)
