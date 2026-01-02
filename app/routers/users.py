from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.user import User, USER_TYPE, UserUpdate
from app.schemas.user import UserCreate, UserResponse, UserResponseName
from app.routers.auth import check_admin, get_current_user

router = APIRouter()

admin_router = APIRouter(prefix="/admin", tags=["Admin - Users"], dependencies=[Depends(check_admin)])
router_develop = APIRouter(tags=["development"], prefix="/develop")

@admin_router.put("/users/{user_id}")
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db)
):
    # Buscar el usuario por ID
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verificar si el nuevo email ya existe en otro usuario
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email, 
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Actualizar solo los campos permitidos
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(db_user, field) and field in ['email', 'name']:
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User updated successfully"}

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exist")

    new_user = User(email=user.email, name=user.name, user_type_id = USER_TYPE["Student"])
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    return new_user

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario autenticado.
    """
    if not isinstance(current_user.id, int) or not isinstance(current_user.email, str) or not isinstance(current_user.name, str) :
        return "Error de tipo con las propiedades"

    return UserResponse(id=current_user.id, email=current_user.email, name=current_user.name)

@router.get("/getName", response_model=UserResponseName)
def get_current_user_name(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario autenticado.
    """
    if not isinstance(current_user.name, str):
        return "Error la propiedad name no es de tipo string"

    return UserResponseName(name=current_user.name)

# Only for development
@router_develop.get("/getAll", response_model=List[UserResponse],
            summary="Obtener todos los usuarios",
            description="Devuelve una lista de todos los usuarios registrados.")
def get_all_users(db: Session = Depends(get_db)):
    """
    Obtiene todos los usuarios registrados.

    **Respuesta:**
    - Lista de usuarios con `id`, `email`, y `name`.
    """
    users = db.query(User).all()
    return users

@router_develop.get("/get/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not isinstance(user.id, int) or not isinstance(user.email, str) or not isinstance(user.name, str) :
        return "Error de tipo con las propiedades"

    return UserResponse(id=user.id, email=user.email, name=user.name)
