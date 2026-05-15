from fastapi import APIRouter,WebSocket,WebSocketDisconnect,Depends,UploadFile,File,Form
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent,AgentExecutor,tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, TextLoader, UnstructuredExcelLoader,Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
import os
import asyncio
import uuid
from app.core.config import settings
from app.tools.zy import *
from app.utils.auth import *
from app.core.logger import get_logger
from app.core.prompt import SYSTEM_PROMPT, MOODS, EMOTION_PROMPT, MEMORY_SUMMARY_PROMPT
from app.schemas.user_schema import *
from typing import List
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from docx import Document
import io


router = APIRouter(tags=["agent"])
logger = get_logger()

class Master:
    def __init__(self):
        self.chatmodel = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=0,
            streaming=True,
        )
        self.QingXu = "default"
        self.MEMORY_KEY = "chat_history"
        self.SYSTEMPL = SYSTEM_PROMPT
        self.MOODS = MOODS

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                   "system",
                   self.SYSTEMPL.format(who_you_are=self.MOODS[self.QingXu]["roleSet"]),
                ),
                MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ],
        )

        tools = [tcm_diagnosis, tcm_prescription, tcm_herbs_info, tcm_acupuncture]
        agent = create_openai_tools_agent(
            self.chatmodel,
            tools=tools,
            prompt=self.prompt,
        )
        self.memory = self.get_memory()
        memory = ConversationBufferMemory(
            llm = self.chatmodel,
            human_prefix="患者",
            ai_prefix="徐大夫",
            memory_key=self.MEMORY_KEY,
            output_key="output",
            return_messages=True,
            max_token_limit=1000,
            chat_memory=self.memory,
        )
        self.agent_executor = AgentExecutor(
            agent = agent,
            tools=tools,
            memory=memory,
            verbose=True,
        )

    def get_memory(self):
        chat_message_history = RedisChatMessageHistory(
            url=settings.REDIS_URL,session_id="session"
        )
        logger.info("chat_message_history:",chat_message_history.messages)
        store_message = chat_message_history.messages
        if len(store_message) > 10:
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        self.SYSTEMPL + "\n" + MEMORY_SUMMARY_PROMPT
                    ),
                    ("user","{input}"),
                ]
            )
            chain = prompt | self.chatmodel
            summary = chain.invoke({"input":store_message,"who_you_are":self.MOODS[self.QingXu]["roleSet"]})
            logger.info("summary:",summary)
            chat_message_history.clear()
            chat_message_history.add_message(summary)
            logger.info("总结后：",chat_message_history.messages)
        return chat_message_history

    def run(self,query):
        qingxu = self.qingxu_chain(query)
        result = self.agent_executor.invoke({"input":query,"chat_history":self.memory.messages})
        return result

    def qingxu_chain(self,query:str):
        chain = ChatPromptTemplate.from_template(EMOTION_PROMPT) | self.chatmodel | StrOutputParser()
        result = chain.invoke({"query":query})
        self.QingXu = result
        print("情绪判断结果:",result)
        return result


@router.post("/agent", response_model=ResponseModel)
async def agent(
    query: TextRequest,
    claims: dict = Depends(verify_api_key)
) -> ResponseModel:
    """
    处理用户输入并返回 AI 助手的回复

    Args:
        query (TextRequest): 包含用户输入内容的请求体
        claims (dict): API 密钥验证信息

    Returns:
        ResponseModel: 包含以下字段的响应
            - code: 响应代码（1表示成功，0表示失败）
            - message: 响应消息
            - data: 包含 AI 回复的字典

    Raises:
        HTTPException: 当处理过程中发生错误时抛出
    """
    try:
        logger.info(f"收到用户查询: {query.content}")
        master = Master()
        result = master.run(query.content)
        logger.info(f"AI 回复生成成功，内容长度: {len(str(result))}")
        return success_resp(
            message="AI 回复生成成功",
            data={
                "msg": result,
                "timestamp": datetime.now().isoformat(),
                "query_length": len(query.content),
                "response_length": len(str(result))
            }
        )
    except Exception as e:
        logger.error(f"处理用户查询时发生错误: {str(e)}")
        # 返回错误响应
        return error_resp(
            message=f"处理用户查询时发生错误: {str(e)}",
            data={
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/add_urls")
async def add_urls(
    url: str = Form(..., description="要添加的URL地址"),
    current_user: User = Depends(get_current_active_user)
):
    """
    添加 URL 内容到向量数据库

    Args:
        url: 要添加的URL地址
        claims: API密钥验证信息
    """
    try:
        logger.info(f"开始处理URL: {url}")

        # 加载网页内容
        loader = WebBaseLoader(url)
        docs = loader.load()

        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=50,
        )
        split_docs = text_splitter.split_documents(docs)

        # 添加到向量数据库
        if split_docs:
            # 初始化 Qdrant 客户端
            qdrant_client = QdrantClient(
                path=settings.QDRANT_PATH
            )

            # 删除已存在的集合（如果有）
            try:
                qdrant_client.delete_collection(collection_name=settings.QDRANT_NAME)
            except Exception:
                pass

            # 创建新的集合
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_NAME,
                vectors_config=VectorParams(
                    size=512,  # BAAI/bge-small-zh-v1.5 模型的维度
                    distance=Distance.COSINE
                )
            )

            # 使用 Hugging Face 的 Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文模型
                model_kwargs={"device": "cpu"},
                cache_folder=settings.MODEL_CACHE_PATH,  # 模型缓存路径
                encode_kwargs={"normalize_embeddings": True}
            )

            # 创建向量存储
            vector_store = Qdrant(
                client=qdrant_client,
                collection_name=settings.QDRANT_NAME,
                embeddings=embeddings
            )

            # 添加文档
            vector_store.add_documents(split_docs)
            logger.info(f"成功添加 {len(split_docs)} 个文档到向量数据库")

        return success_resp(message="URL内容添加成功", data={"doc_count": len(split_docs)})
    except Exception as e:
        logger.error(f"添加URL内容失败: {str(e)}")
        return error_resp(message=f"添加URL内容失败: {str(e)}")

@router.post("/add_pdfs")
async def add_pdfs(files: List[UploadFile] = File(...), claims: dict = Depends(verify_api_key)):
    """
    上传 PDF 文件并添加到向量数据库
    """
    try:
        # 创建临时目录存储上传的文件
        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True)

        all_docs = []
        for file in files:
            # 保存上传的文件
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 加载 PDF 文件
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=50,
            )
            split_docs = text_splitter.split_documents(docs)
            all_docs.extend(split_docs)

            # 删除临时文件
            os.remove(file_path)

        # 添加到向量数据库
        if all_docs:
            # 初始化 Qdrant 客户端
            qdrant_client = QdrantClient(
                path=settings.QDRANT_PATH
            )

            # 删除已存在的集合（如果有）
            try:
                qdrant_client.delete_collection(collection_name=settings.QDRANT_NAME)
            except Exception:
                pass

            # 创建新的集合
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_NAME,
                vectors_config=VectorParams(
                    size=512,  # BAAI/bge-small-zh-v1.5 模型的维度
                    distance=Distance.COSINE
                )
            )

            # 使用 Hugging Face 的 Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文模型
                model_kwargs={"device": "cpu"},
                cache_folder=settings.MODEL_CACHE_PATH,  # 模型缓存路径
                encode_kwargs={"normalize_embeddings": True}
            )

            # 创建向量存储
            vector_store = Qdrant(
                client=qdrant_client,
                collection_name=settings.QDRANT_NAME,
                embeddings=embeddings
            )

            # 添加文档
            vector_store.add_documents(all_docs)
            logger.info(f"成功添加 {len(all_docs)} 个文档到向量数据库")

        # 删除临时目录
        os.rmdir(temp_dir)

        return success_resp(message="PDF文件添加成功", data={"doc_count": len(all_docs)})
    except Exception as e:
        logger.error(f"添加PDF文件失败: {str(e)}")
        return error_resp(message=f"添加PDF文件失败: {str(e)}")

@router.post("/add_texts")
async def add_texts(files: List[UploadFile] = File(...), claims: dict = Depends(verify_api_key)):
    """
    上传 txt 文件并添加到向量数据库

    Args:
        files: 上传的 txt 文件列表
        claims: API 密钥验证信息
    """
    try:
        all_docs = []
        for file in files:
            # 检查文件类型
            if not file.filename.endswith('.txt'):
                return error_resp(message=f"文件 {file.filename} 不是 txt 格式")

            # 读取文件内容
            content = await file.read()
            try:
                # 尝试解码为 UTF-8
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                # 如果 UTF-8 解码失败，尝试其他编码
                try:
                    text = content.decode('gbk')
                except UnicodeDecodeError:
                    return error_resp(message=f"文件 {file.filename} 编码格式不支持")

            # 创建临时文件
            temp_file = f"temp_{uuid.uuid4()}.txt"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(text)

            # 加载文本文件
            loader = TextLoader(temp_file)
            docs = loader.load()

            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=50,
            )
            split_docs = text_splitter.split_documents(docs)
            all_docs.extend(split_docs)

            # 删除临时文件
            os.remove(temp_file)

        # 添加到向量数据库
        if all_docs:
            # 初始化 Qdrant 客户端
            qdrant_client = QdrantClient(
                path=settings.QDRANT_PATH
            )

            # 删除已存在的集合（如果有）
            try:
                qdrant_client.delete_collection(collection_name=settings.QDRANT_NAME)
            except Exception:
                pass

            # 创建新的集合
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_NAME,
                vectors_config=VectorParams(
                    size=512,  # BAAI/bge-small-zh-v1.5 模型的维度
                    distance=Distance.COSINE
                )
            )

            # 使用 Hugging Face 的 Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文模型
                model_kwargs={"device": "cpu"},
                cache_folder=settings.MODEL_CACHE_PATH,  # 模型缓存路径
                encode_kwargs={"normalize_embeddings": True}
            )

            # 创建向量存储
            vector_store = Qdrant(
                client=qdrant_client,
                collection_name=settings.QDRANT_NAME,
                embeddings=embeddings
            )

            # 添加文档
            vector_store.add_documents(all_docs)
            logger.info(f"成功添加 {len(all_docs)} 个文本到向量数据库")

        return success_resp(message="文本文件添加成功", data={"doc_count": len(all_docs)})
    except Exception as e:
        logger.error(f"添加文本文件失败: {str(e)}")
        return error_resp(message=f"添加文本文件失败: {str(e)}")

@router.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...), current_user: User = Depends(get_current_active_user)):
    """
    统一文件上传接口，支持多种文件格式（PDF、TXT、DOC、DOCX）

    Args:
        files: 上传的文件列表
        claims: API 密钥验证信息
    """
    try:
        all_docs = []
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        for file in files:
            # 检查文件类型
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ['.pdf', '.txt', '.doc', '.docx']:
                return error_resp(message=f"不支持的文件格式: {file_extension}")

            # 保存上传的文件
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 根据文件类型选择不同的加载器
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            elif file_extension == '.docx':
                loader = Docx2txtLoader(file_path)
            elif file_extension == '.xlsx':
                loader = UnstructuredExcelLoader(file_path)

            # 加载文档
            docs = loader.load()

            # 文本分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=50,
            )
            split_docs = text_splitter.split_documents(docs)
            all_docs.extend(split_docs)

            # 删除临时文件
            # os.remove(file_path)

        # 添加到向量数据库
        if all_docs:
            # 初始化 Qdrant 客户端
            qdrant_client = QdrantClient(
                path=settings.QDRANT_PATH
            )

            # 删除已存在的集合（如果有）
            try:
                qdrant_client.delete_collection(collection_name=settings.QDRANT_NAME)
            except Exception:
                pass

            # 创建新的集合
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_NAME,
                vectors_config=VectorParams(
                    size=512,  # BAAI/bge-small-zh-v1.5 模型的维度
                    distance=Distance.COSINE
                )
            )

            # 使用 Hugging Face 的 Embeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-zh-v1.5",  # 中文模型
                model_kwargs={"device": "cpu"},
                cache_folder=settings.MODEL_CACHE_PATH,  # 模型缓存路径
                encode_kwargs={"normalize_embeddings": True}
            )

            # 创建向量存储
            vector_store = Qdrant(
                client=qdrant_client,
                collection_name=settings.QDRANT_NAME,
                embeddings=embeddings
            )

            # 添加文档
            vector_store.add_documents(all_docs)
            logger.info(f"成功添加 {len(all_docs)} 个文档到向量数据库")

        # 删除临时目录
        # os.rmdir(temp_dir)

        return success_resp(message="文件上传成功", data={"doc_count": len(all_docs)})
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return error_resp(message=f"文件上传失败: {str(e)}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Connection closed")
        await websocket.close()