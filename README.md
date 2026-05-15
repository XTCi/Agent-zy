# 中医智能体管理系统

> 本科毕业设计

一个面向中医领域的 AI 智能体管理平台。用户可以创建具有个性化角色设定的中医智能体，智能体内置辨证诊断、中药处方、针灸方案、药材查询等专业工具，并支持基于私有知识库的 RAG 检索增强对话。

---

## 系统架构

```
Agent-zy/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── agent.py  # 智能体管理 + WebSocket 对话 + 知识库构建
│   │   │   ├── chat.py   # 轻量对话接口
│   │   │   └── user.py   # 用户认证
│   │   ├── core/
│   │   │   ├── config.py    # 环境变量读取（pydantic-settings）
│   │   │   ├── database.py  # SQLAlchemy MySQL 连接
│   │   │   ├── prompt.py    # 系统提示词 / 情绪模板 / 工具提示词
│   │   │   └── logger.py    # Loguru 日志
│   │   ├── tools/
│   │   │   └── zy.py     # 中医专属 LangChain 工具集
│   │   └── utils/
│   │       ├── auth.py   # JWT 认证
│   │       └── websocket.py
│   ├── requirements.txt
│   ├── agent.sql         # 数据库建表脚本
│   └── Dockerfile
└── frontend/             # Vue3 前端
    ├── src/
    │   ├── views/AgentManager/  # 智能体管理页面
    │   ├── views/Chat.vue       # 对话界面
    │   ├── api/                 # Axios 接口封装
    │   └── router/
    └── package.json
```

---

## 功能特性

**智能体管理**
- 创建/编辑/删除个性化智能体，支持自定义角色设定、对话温度、头像上传
- 每个用户最多创建 10 个智能体

**中医专属工具（LangChain Agent Tools）**

| 工具 | 说明 |
|------|------|
| `tcm_diagnosis` | 根据症状进行中医辨证诊断 |
| `tcm_prescription` | 根据诊断结果开具中药处方 |
| `tcm_herbs_info` | 查询中药材详细信息 |
| `tcm_acupuncture` | 根据症状生成针灸治疗方案 |
| `get_info_from_local_db` | 从私有知识库进行 RAG 语义检索 |
| `xsearch` | SerpAPI 实时网络搜索 |

**知识库构建（RAG）**
- 支持网页 URL 抓取、PDF、TXT、DOCX、XLSX 文件上传
- Embedding：`BAAI/bge-small-zh-v1.5`（中文语义向量，本地运行）
- 向量存储：Qdrant（本地文件模式，无需服务端）

**对话与记忆**
- WebSocket 实时流式对话
- 对话历史持久化到 Redis（按 `user_{id}_agent_{id}` 分 session）
- 超过 10 条消息自动触发 LLM 摘要压缩，节省 Token

**情绪感知**
- 对话中自动检测用户情绪，动态调整智能体回复风格

**用户系统**
- 注册/登录、JWT Token 认证、个人中心

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 · Vite · Element Plus · Vue Router · Pinia · Axios |
| 后端 | FastAPI · LangChain · SQLAlchemy · Pydantic v2 |
| 对话模型 | 阿里云百炼 `qwen-plus`（OpenAI 兼容接口） |
| Embedding | `BAAI/bge-small-zh-v1.5`（HuggingFace，本地推理） |
| 向量数据库 | Qdrant（本地文件模式） |
| 关系数据库 | MySQL 8 |
| 会话记忆 | Redis |
| 实时通信 | WebSocket |
| 日志 | Loguru |
| 容器化 | Docker |

---

## 快速开始

### 前置依赖

需要本地运行以下服务：

- **MySQL 8**：存储用户、智能体数据
- **Redis**：存储对话历史
- **Python 3.10+**
- **Node.js 16+**

> Qdrant 使用本地文件模式，无需额外安装。
> Embedding 模型首次运行时会自动从 HuggingFace 下载到 `local_model/` 目录。

---

### 后端启动

```bash
cd backend

# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
mysql -u root -p < agent.sql

# 3. 配置环境变量（见下方说明）
cp .env.example .env.local

# 4. 启动服务（默认加载 .env.local）
RUN_MOD=local uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档：http://localhost:8000/docs

---

### 前端启动

```bash
cd frontend

npm install
npm run dev
# 访问 http://localhost:5173
```

---

### Docker 部署（后端）

```bash
cd backend
docker build -t agent-zy-backend .
docker run -d -p 8000:8000 \
  --env-file .env.local \
  -e RUN_MOD=local \
  agent-zy-backend
```

---

## 环境变量配置

后端通过 `RUN_MOD` 环境变量决定读取哪个配置文件：
- `RUN_MOD=local` → 读取 `.env.local`
- `RUN_MOD=prod` → 读取 `.env.prod`

在 `backend/` 目录下创建 `.env.local`：

```env
# ===== 模型 API（阿里云百炼）=====
# 控制台获取：https://bailian.console.aliyun.com/
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus          # 可选：qwen-max / qwen-turbo / qwen-plus

# ===== JWT 认证 =====
JWT_SECRET_KEY=your_random_secret_key_here   # 随机字符串，用于签发 Token
API_SECRET_KEY=your_api_secret_key_here      # 内部接口鉴权密钥

# ===== 数据库 =====
DATABASE_URL=mysql://root:your_password@localhost:3306/xu

# ===== Redis（对话历史存储）=====
REDIS_URL=redis://localhost:6379/0

# ===== Qdrant（知识库向量存储）=====
QDRANT_PATH=local_qdrant        # 本地存储目录（相对于 backend/）
QDRANT_NAME=local_documents     # Collection 名称

# ===== Embedding 模型缓存 =====
MODEL_CACHE_PATH=local_model    # HuggingFace 模型本地缓存目录

# ===== 实时搜索（可选）=====
# 注册获取：https://serpapi.com/
SERPAPI_API_KEY=your_serpapi_key

# ===== 应用配置 =====
APP_NAME=FastAPI LLM Service
APP_VERSION=1.0.0
DEBUG=True
ALLOW_ORIGINS=["*"]

# ===== 日志 =====
LOG_LEVEL=INFO
LOG_FORMAT={time:YYYY-MM-DD HH:mm:ss} | {level} | {message}
LOG_FILE=logs/app.log

# ===== LangSmith 链路追踪（可选）=====
# 注册获取：https://smith.langchain.com/
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=ls__xxxxxxxx
LANGCHAIN_PROJECT=your_project_name
```

---

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/user/register` | 注册 |
| POST | `/api/user/login` | 登录，返回 JWT Token |
| GET | `/api/chat/agent_list` | 获取我的智能体列表 |
| POST | `/api/chat/create_agent` | 创建智能体 |
| PUT | `/api/chat/update_agent/{id}` | 更新智能体 |
| DELETE | `/api/chat/delete_agent/{id}` | 删除智能体 |
| POST | `/api/chat/chat_with_agent/{id}` | 与智能体对话（HTTP） |
| WebSocket | `/ws/{agent_id}` | 实时流式对话 |
| POST | `/api/add_urls` | 网页 URL 加入知识库 |
| POST | `/api/add_pdfs` | PDF 加入知识库 |
| POST | `/api/add_texts` | TXT 加入知识库 |
| POST | `/api/chat/upload_photo` | 上传智能体头像 |

完整接口文档启动服务后访问：http://localhost:8000/docs

---

## 毕业论文

如需查阅对应的毕业设计论文，欢迎联系作者：

- 邮箱：xutc2002@gmail.com

---

## 许可证

[MIT License](LICENSE)
