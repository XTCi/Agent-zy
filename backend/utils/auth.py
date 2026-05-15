from typing import Optional
from fastapi import Request, HTTPException, Depends
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from datetime import timedelta, datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user_model import *
from app.core.database import get_db

# JWT配置
JWT_SECRET = settings.JWT_SECRET_KEY
API_SECRET_KEY = settings.API_SECRET_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_api_key(request: Request) -> bool:
    authorization = request.headers.get("Authorization")
    if authorization != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Missing authorization header")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing authorization header")

    try:
        # 分割 Bearer token
        parts = authorization.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authorization header format")

        token = parts[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=403, detail="Invalid token")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=403, detail="User not found")

        return user

    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid user ID in token")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user