# FastAPI 智能助手

基于 FastAPI 开发的智能对话助手系统，支持多智能体管理、实时对话、知识库检索等功能。

## 功能特性

- 智能体管理

  - 创建、更新、删除智能体
  - 自定义智能体名称、角色设定、开场白等
  - 支持知识库关联
- 实时对话

  - 基于 WebSocket 的实时对话
  - 支持流式响应
  - 对话历史记录管理
- 知识库检索

  - 智能匹配相关知识
  - 可配置检索阈值
  - 支持仅知识库模式

## 技术架构

- 后端框架：FastAPI
- 对话模型：阿里云 DashScope
- 数据库：SQLAlchemy ORM
- 实时通信：WebSocket
- 容器化：Docker

## 环境要求

- Python 3.7+
- Docker（可选）

## 快速开始

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置环境变量

创建 .env 文件并配置以下参数：

```env
DASHSCOPE_API_KEY=your_api_key
ALI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
WORKSPACE_ID=your_workspace_id
```

3. 启动服务

- 环境分 local,alpha,prod
- 配置环境变量RUN_MOD=local，获取配置文件, 默认生产环境配置

#### 手动启动
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

```
#### pycharm 启动
调试main.py
![img.png](doc/img.png)

## Docker 部署

1. 构建镜像

```bash
docker build -t fastapi-assistant .
```

2. 运行容器

```bash
docker run -d -p 8000:8000 fastapi-assistant
```

## API 文档

启动服务后访问：http://localhost:8000/docs

### 主要接口

- POST `/assistant/create` - 创建智能体
- POST `/assistant/update` - 更新智能体
- GET `/assistant/list` - 获取智能体列表
- WebSocket `/ws/{assistant_id}` - 智能体实时对话
- POST `/assitant_chat` - 智能体对话

## 开发说明

### 项目结构

```
app/
├── auth.py         # 认证相关
├── balian.py       # 百炼API封装
├── bc_assistant.py # 智能体核心逻辑
├── config.py      # 配置管理
├── database.py    # 数据库配置
├── main.py        # 主程序入口
├── models.py      # 数据模型
├── schemas.py     # 数据验证
├── tools.py       # 工具函数
└── websocket.py   # WebSocket处理
```

### 核心功能

1. 智能体管理

- 支持自定义智能体属性
- 关联知识库配置
- 对话参数调整

2. 实时对话

- WebSocket长连接
- 支持流式输出
- 自动重连机制

3. 知识库检索

- 向量检索
- 相似度阈值控制
- 知识库更新
