from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    photo = Column(String(255), nullable=False, default="")
    introduce = Column(Text, nullable=False)
    role_setting = Column(Text, nullable=False)
    prologue = Column(Text, nullable=False)
    is_delete = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    agent_id = Column(String(50), unique=True, nullable=False)
    temperature = Column(Float, nullable=False, default=0.0)