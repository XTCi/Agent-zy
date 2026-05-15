from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from sqlalchemy.sql import func

from app.core.database import get_db
from app.models.user_model import *
from app.schemas.user_schema import *
from app.crud.user_crud import *
from app.utils.auth import create_access_token, get_current_active_user
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=ResponseModel)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # Check if email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )

    created_user = create_user(db=db, user=user)
    # 将 SQLAlchemy User 对象转换为 Pydantic UserResponse 对象
    user_response = UserResponse.model_validate(created_user)
    return success_resp(message="用户注册成功", data={"user": user_response})

@router.post("/login", response_model=ResponseModel)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login time
    user.last_login = func.now()
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user_id=user.id, expires_delta=access_token_expires
    )
    # 将 SQLAlchemy User 对象转换为 Pydantic UserResponse 对象
    user_response = UserResponse.model_validate(user)
    return success_resp(
        message="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    )

@router.get("/me", response_model=ResponseModel)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    # 将 SQLAlchemy User 对象转换为 Pydantic UserResponse 对象
    user_response = UserResponse.model_validate(current_user)
    return success_resp(message="用户信息获取成功", data={"user": user_response})

@router.put("/me", response_model=ResponseModel)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    updated_user = update_user(db=db, user_id=current_user.id, user_update=user_update)
    # 将 SQLAlchemy User 对象转换为 Pydantic UserResponse 对象
    user_response = UserResponse.model_validate(updated_user)
    return success_resp(message="用户更新成功", data={"user": user_response})

@router.delete("/me", response_model=ResponseModel)
def delete_user_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    delete_user(db=db, user_id=current_user.id)
    return success_resp(message="用户删除成功")
