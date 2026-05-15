from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    photo: Optional[str] = Field(default="")
    introduce: str = Field(..., min_length=1)
    role_setting: str = Field(..., min_length=1)
    prologue: str = Field(..., min_length=1)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    photo: Optional[str] = None
    introduce: Optional[str] = Field(None, min_length=1)
    role_setting: Optional[str] = Field(None, min_length=1)
    prologue: Optional[str] = Field(None, min_length=1)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)

class AgentResponse(AgentBase):
    id: int
    user_id: int
    create_time: datetime
    update_time: datetime
    agent_id: str
    is_delete: bool

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ChatHistory(BaseModel):
    messages: List[ChatMessage]
    total_messages: int
    last_updated: datetime

class TextRequest(BaseModel):
    content: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    message: str
    agent_id: str
    agent_name: str
    timestamp: datetime
    query_length: int
    response_length: int