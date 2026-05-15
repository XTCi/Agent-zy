from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Index
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="用户ID，主键")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名，唯一")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱，唯一")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    full_name = Column(String(100), nullable=True, comment="用户全名")
    phone = Column(String(20), nullable=True, comment="手机号码")
    created_at = Column(DateTime, server_default=func.now(), nullable=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True, comment="更新时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    is_active = Column(Boolean, default=True, nullable=True, comment="账户是否激活")
    role = Column(String(20), default="user", nullable=True, comment="用户角色：user-普通用户，admin-管理员")

    # 定义索引
    __table_args__ = (
        # 用户名和邮箱的复合索引
        Index('idx_username_email', 'username', 'email'),
        # 创建时间的索引
        Index('idx_created_at', 'created_at'),
        # 最后登录时间的索引
        Index('idx_last_login', 'last_login'),
        # 角色和激活状态的复合索引
        Index('idx_role_active', 'role', 'is_active'),
    )