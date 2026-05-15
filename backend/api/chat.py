from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
import shutil
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

from app.core.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import *
from app.schemas.agent_schema import *
from app.crud.agent_crud import (
    create_agent as crud_create_agent,
    get_agent,
    get_agents,
    update_agent,
    delete_agent
)
from app.utils.auth import get_current_active_user
from app.core.config import settings
from app.core.logger import get_logger
from app.tools.zy import *
from app.core.prompt import MEMORY_SUMMARY_PROMPT

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger()

# 创建上传目录
UPLOAD_DIR = "uploads/agents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatMaster:
    def __init__(self, role_setting: str, temperature: float = 0.0, user_id: int = None, agent_id: str = None):
        self.chatmodel = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=temperature,
            streaming=True,
        )
        self.MEMORY_KEY = "chat_history"
        self.SYSTEMPL = role_setting
        self.user_id = user_id
        self.agent_id = agent_id

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.SYSTEMPL),
                MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        tools = [get_info_from_local_db,tcm_diagnosis, tcm_prescription, tcm_herbs_info, tcm_acupuncture]
        agent = create_openai_tools_agent(
            self.chatmodel,
            tools=tools,
            prompt=self.prompt,
        )

        self.memory = self.get_memory()
        memory = ConversationBufferMemory(
            llm=self.chatmodel,
            human_prefix="用户",
            ai_prefix="中医专家",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token_limit=1000,
            chat_memory=self.memory,
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
        )

    def get_memory(self):
        session_id = f"user_{self.user_id}_agent_{self.agent_id}"
        chat_message_history = RedisChatMessageHistory(
            url=settings.REDIS_URL,
            session_id=session_id
        )
        logger.info(f"创建新的对话记忆，会话ID: {session_id}")

        # 检查消息数量，如果超过10条则进行总结
        store_message = chat_message_history.messages
        if len(store_message) > 10:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.SYSTEMPL + "\n" + MEMORY_SUMMARY_PROMPT
                    ),
                    ("user", "{input}"),
                ]
            )
            chain = prompt | self.chatmodel
            summary = chain.invoke({"input": store_message})
            logger.info(f"对话历史总结: {summary}")
            chat_message_history.clear()
            chat_message_history.add_message(summary)
            logger.info("总结后的对话历史已保存")

        return chat_message_history

    def get_chat_history(self) -> List[dict]:
        messages = []
        for msg in self.memory.messages:
            if isinstance(msg, HumanMessage):
                messages.append({
                    "role": "user",
                    "content": msg.content,
                    "timestamp": datetime.now()
                })
            elif isinstance(msg, AIMessage):
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "timestamp": datetime.now()
                })
        return messages

    def clear_history(self):
        self.memory.clear()
        logger.info(f"清除对话历史，会话ID: user_{self.user_id}_agent_{self.agent_id}")

    def run(self, query: str):
        result = self.agent_executor.invoke({
            "input": query,
            "chat_history": self.memory.messages
        })
        return result

@router.post("/create_agent", response_model=ResponseModel)
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新的智能体
    """
    try:
        # 检查用户是否已达到智能体创建上限
        user_agents = get_agents(db, user_id=current_user.id)
        if len(user_agents) >= 10:  # 每个用户最多创建10个智能体
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已达到智能体创建上限"
            )

        # 生成唯一的 agent_id
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        agent_id = f"agent_{timestamp}_{current_user.id}"

        # 创建智能体
        db_agent = crud_create_agent(
            db=db,
            agent=agent,
            user_id=current_user.id,
            agent_id=agent_id
        )

        logger.info(f"用户 {current_user.id} 创建智能体成功: {agent_id}")
        return success_resp(
            message="智能体创建成功",
            data=AgentResponse.model_validate(db_agent).model_dump()
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"创建智能体失败: {str(e)}")
        return error_resp(message=f"创建智能体失败: {str(e)}")

@router.put("/update_agent/{agent_id}", response_model=ResponseModel)
async def update_agent_endpoint(
    agent_id: str,
    agent: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新智能体信息
    """
    try:
        # 检查智能体是否存在且属于当前用户
        db_agent = get_agent(db, agent_id)
        if not db_agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if db_agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权修改此智能体")

        # 更新智能体
        updated_agent = update_agent(db=db, agent_id=agent_id, agent=agent)
        if not updated_agent:
            raise HTTPException(status_code=500, detail="更新智能体失败")

        logger.info(f"用户 {current_user.id} 更新智能体成功: {agent_id}")
        return success_resp(
            message="智能体更新成功",
            data=AgentResponse.model_validate(updated_agent).model_dump()
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"更新智能体失败: {str(e)}")
        return error_resp(message=f"更新智能体失败: {str(e)}")

@router.delete("/delete_agent/{agent_id}", response_model=ResponseModel)
async def delete_agent_endpoint(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除智能体
    """
    try:
        # 检查智能体是否存在且属于当前用户
        db_agent = get_agent(db, agent_id)
        if not db_agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if db_agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此智能体")

        # 删除智能体（软删除）
        success = delete_agent(db=db, agent_id=agent_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除智能体失败")

        # 清理对话历史
        master = ChatMaster(
            role_setting=db_agent.role_setting,
            temperature=db_agent.temperature,
            user_id=current_user.id,
            agent_id=agent_id
        )
        master.clear_history()

        logger.info(f"用户 {current_user.id} 删除智能体成功: {agent_id}")
        return success_resp(message="智能体删除成功")
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"删除智能体失败: {str(e)}")
        return error_resp(message=f"删除智能体失败: {str(e)}")

@router.get("/agent_list", response_model=ResponseModel)
async def agent_list(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    获取用户的智能体列表
    """
    try:
        agents = get_agents(db, user_id=current_user.id, skip=skip, limit=limit)
        total = len(get_agents(db, user_id=current_user.id))  # 获取总数

        return success_resp(
            message="获取智能体列表成功",
            data={
                "total": total,
                "agents": [AgentResponse.model_validate(agent) for agent in agents]
            }
        )
    except Exception as e:
        logger.error(f"获取智能体列表失败: {str(e)}")
        return error_resp(message=f"获取智能体列表失败: {str(e)}")

@router.get("/agent_detail/{agent_id}", response_model=ResponseModel)
async def agent_detail(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取智能体详细信息
    """
    try:
        agent = get_agent(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权查看此智能体")

        return success_resp(
            message="获取智能体详情成功",
            data=AgentResponse.model_validate(agent)
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"获取智能体详情失败: {str(e)}")
        return error_resp(message=f"获取智能体详情失败: {str(e)}")

@router.post("/chat_with_agent/{agent_id}", response_model=ResponseModel)
async def chat_with_agent(
    agent_id: str,
    query: TextRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    与指定智能体进行对话
    """
    try:
        agent = get_agent(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此智能体")

        master = ChatMaster(
            role_setting=agent.role_setting,
            temperature=agent.temperature,
            user_id=current_user.id,
            agent_id=agent_id
        )

        result = master.run(query.content)
        # 从返回结果中提取消息内容
        if isinstance(result, dict) and 'output' in result:
            message = result['output']
        else:
            message = str(result)

        logger.info(f"用户 {current_user.id} 与智能体 {agent_id} 对话成功")
        return success_resp(
            message="对话成功",
            data=ChatResponse(
                message=message,
                agent_id=agent_id,
                agent_name=agent.name,
                timestamp=datetime.now(),
                query_length=len(query.content),
                response_length=len(message)
            ).model_dump()
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"与智能体 {agent_id} 对话时发生错误: {str(e)}")
        return error_resp(message=f"对话失败: {str(e)}")

@router.get("/chat_history/{agent_id}", response_model=ResponseModel)
async def get_chat_history(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取与指定智能体的对话历史
    """
    try:
        agent = get_agent(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此智能体")

        master = ChatMaster(
            role_setting=agent.role_setting,
            temperature=agent.temperature,
            user_id=current_user.id,
            agent_id=agent_id
        )

        messages = master.get_chat_history()
        return success_resp(
            message="获取对话历史成功",
            data=ChatHistory(
                messages=messages,
                total_messages=len(messages),
                last_updated=datetime.now()
            ).model_dump()
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"获取对话历史时发生错误: {str(e)}")
        return error_resp(message=f"获取对话历史失败: {str(e)}")

@router.delete("/chat_history/{agent_id}", response_model=ResponseModel)
async def clear_chat_history(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    清除与指定智能体的对话历史
    """
    try:
        agent = get_agent(db, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="智能体不存在")
        if agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此智能体")

        master = ChatMaster(
            role_setting=agent.role_setting,
            temperature=agent.temperature,
            user_id=current_user.id,
            agent_id=agent_id
        )

        master.clear_history()
        logger.info(f"用户 {current_user.id} 清除智能体 {agent_id} 的对话历史成功")
        return success_resp(message="清除对话历史成功")
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"清除对话历史时发生错误: {str(e)}")
        return error_resp(message=f"清除对话历史失败: {str(e)}")

@router.post("/upload_photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传智能体头像
    """
    try:
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请上传图片文件"
            )

        # 获取文件扩展名
        file_extension = os.path.splitext(file.filename)[1]
        if not file_extension:
            # 根据content_type设置默认扩展名
            if file.content_type == 'image/jpeg':
                file_extension = '.jpg'
            elif file.content_type == 'image/png':
                file_extension = '.png'
            elif file.content_type == 'image/gif':
                file_extension = '.gif'
            else:
                file_extension = '.jpg'  # 默认使用jpg

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"agent_photo_{current_user.id}_{timestamp}{file_extension}"

        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 返回文件URL
        photo_url = f"/uploads/agents/{filename}"
        logger.info(f"用户 {current_user.id} 上传头像成功: {photo_url}")
        return success_resp(
            message="头像上传成功",
            data={"photo_url": photo_url}
        )
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}")
        return error_resp(message=f"上传头像失败: {str(e)}")

@router.get("/photo/{filename}")
async def get_photo(filename: str):
    """
    获取智能体头像
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="头像文件不存在"
            )
        return FileResponse(file_path)
    except HTTPException as e:
        return error_resp(message=str(e.detail))
    except Exception as e:
        logger.error(f"获取头像失败: {str(e)}")
        return error_resp(message=f"获取头像失败: {str(e)}")