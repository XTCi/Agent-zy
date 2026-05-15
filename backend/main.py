from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api import chat, agent, user

app = FastAPI(
    title="agent-zy",
    description="中医对话助手",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 允许的域名列表
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite 开发服务器默认端口
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000"
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 设置允许的域名
    allow_credentials=True,  # 是否允许发送 Cookie
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的请求头
)

# 创建上传目录
os.makedirs("uploads/agents", exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(chat.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(user.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Agent API"}
