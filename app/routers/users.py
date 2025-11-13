from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from uuid import UUID
from werkzeug.security import generate_password_hash, check_password_hash

router = APIRouter()

# CREATE - Создание пользователя
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка на существующего пользователя
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Хэшируем пароль и создаем пользователя
    hashed_password = generate_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# READ - Получение всех пользователей
@router.get("/", response_model=list[schemas.UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# READ - Получение пользователя по ID
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(models.User).filter(models.User.user_id == user_uuid).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# UPDATE - Обновление пользователя
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: str, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    db_user = db.query(models.User).filter(models.User.user_id == user_uuid).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем только переданные поля
    update_data = user_update.dict(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['password_hash'] = generate_password_hash(update_data.pop('password'))
    
    if 'email' in update_data:
        # Проверяем, что email не занят другим пользователем
        existing_user = db.query(models.User).filter(
            models.User.email == update_data['email'],
            models.User.user_id != user_uuid
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    if 'username' in update_data:
        # Проверяем, что username не занят другим пользователем
        existing_user = db.query(models.User).filter(
            models.User.username == update_data['username'],
            models.User.user_id != user_uuid
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE - Удаление пользователя
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    db_user = db.query(models.User).filter(models.User.user_id == user_uuid).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None

# Функция для проверки пароля (для будущей аутентификации)
def verify_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)