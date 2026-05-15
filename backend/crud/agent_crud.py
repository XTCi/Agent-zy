from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.models.agent_model import Agent
from app.schemas.agent_schema import AgentCreate, AgentUpdate

def create_agent(db: Session, agent: AgentCreate, user_id: int, agent_id: str) -> Agent:
    """
    创建新的智能体
    """
    db_agent = Agent(
        name=agent.name,
        photo=agent.photo,
        introduce=agent.introduce,
        role_setting=agent.role_setting,
        prologue=agent.prologue,
        temperature=agent.temperature,
        user_id=user_id,
        agent_id=agent_id,
        is_delete=False
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
    """
    根据 agent_id 获取智能体
    """
    return db.query(Agent).filter(
        and_(
            Agent.agent_id == agent_id,
            Agent.is_delete == False
        )
    ).first()

def get_agents(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Agent]:
    """
    获取用户的所有智能体列表
    """
    return db.query(Agent).filter(
        and_(
            Agent.user_id == user_id,
            Agent.is_delete == False
        )
    ).offset(skip).limit(limit).all()

def update_agent(db: Session, agent_id: str, agent: AgentUpdate) -> Optional[Agent]:
    """
    更新智能体信息
    """
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None

    update_data = agent.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)

    db_agent.update_time = datetime.now()
    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: str) -> bool:
    """
    软删除智能体
    """
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return False

    db_agent.is_delete = True
    db_agent.update_time = datetime.now()
    db.commit()
    return True