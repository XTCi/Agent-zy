from fastapi import FastAPI
from app.api import chat, agent
app = FastAPI(
    title="agent-zy",
    description="中医对话助手",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",

)

app.include_router(chat.router, prefix="/api")
app.include_router(agent.router, prefix="/api")

