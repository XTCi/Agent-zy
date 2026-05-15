# 第一阶段：安装 Python 依赖并创建基础镜像
FROM python:3.11-slim

# 删除原有的 /app 目录
RUN rm -rf /app/*

# 设置工作目录为 /app
WORKDIR /app

# 1. 安装系统依赖（关键修复步骤）
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 到容器中
COPY requirements.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade-strategy only-if-needed -r requirements.txt

# 复制当前项目代码到容器的 /app 目录
COPY . /app/

# 暴露 FastAPI 应用默认的端口
EXPOSE 8000

# 启动 FastAPI 应用，使用 Uvicorn 运行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]