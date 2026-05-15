from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
#工具
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import JsonOutputParser
from langchain.tools import tool
from typing import Optional, Dict, List
from app.core.prompt import TOOL_PROMPTS
from app.core.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

# 初始化你的LoRA微调模型
chat_model = ChatOpenAI(
    model=settings.OPENAI_MODEL,  # 从配置文件中获取模型名称
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE,
    temperature=0,
    streaming=True,
)

@tool
def test():
    """Test tool"""
    return "test"

@tool
def xsearch(query:str):
    """只有需要了解实时信息或不知道的事情的时候才会使用这个工具。"""
    serp = SerpAPIWrapper()
    result = serp.run(query)
    print("实时搜索结果:",result)
    return result

@tool
def get_info_from_local_db(query:str):
    """只有当用户指明要使用知识库回答的时候才会使用这个工具"""
    try:
        # 初始化 Qdrant 客户端
        qdrant_client = QdrantClient(
            path=settings.QDRANT_PATH
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
        # 创建检索器
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4}  # 返回最相关的4个文档
        )
        # 执行检索
        result = retriever.get_relevant_documents(query)
        return result
    except Exception as e:
        logger.error(f"从本地数据库检索信息失败: {str(e)}")
        return []

@tool
def tcm_diagnosis(symptoms: str) -> str:
    """根据患者描述的症状进行中医诊断和辨证。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["diagnosis"]),
        ("user", f"患者症状描述：{symptoms}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result

@tool
def tcm_prescription(diagnosis: str) -> str:
    """根据中医诊断开具处方。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["prescription"]),
        ("user", f"诊断结果：{diagnosis}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result

@tool
def tcm_herbs_info(herb_name: str) -> str:
    """查询中药材的详细信息。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["herbs_info"]),
        ("user", f"查询药材：{herb_name}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result

@tool
def tcm_acupuncture(symptoms: str) -> str:
    """根据症状提供针灸治疗方案。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["acupuncture"]),
        ("user", f"患者症状：{symptoms}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result

@tool
def tcm_dietary_advice(symptoms: str) -> str:
    """根据症状提供饮食调养建议。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["dietary_advice"]),
        ("user", f"患者症状：{symptoms}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result

@tool
def tcm_classic_quote(query: str) -> str:
    """查询中医经典著作中的相关内容。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", TOOL_PROMPTS["classic_quote"]),
        ("user", f"查询内容：{query}")
    ])
    chain = prompt | chat_model | JsonOutputParser()
    result = chain.invoke({})
    return result