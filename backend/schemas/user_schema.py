from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional
from datetime import datetime

# 用户注册请求模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")

# 用户登录请求模型
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

# 用户更新请求模型
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    password: Optional[str] = Field(None, min_length=6, description="新密码")

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    role: str

    class Config:
        from_attributes = True

# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Token 数据模型
class TokenData(BaseModel):
    username: Optional[str] = None

# 文本请求模型
class TextRequest(BaseModel):
    content: str = Field(..., description="用户输入内容")

# 统一响应模型
class ResponseModel(BaseModel):
    code: int
    message: str
    data: dict = {}

    class Config:
        from_attributes = True

def success_resp(message="", data={}):
    return ResponseModel(code=1, message=message, data=data)

def error_resp(data={}, message=""):
    return ResponseModel(code=0, message=message, data=data)