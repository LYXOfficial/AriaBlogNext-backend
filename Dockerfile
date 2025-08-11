FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml .

# 安装依赖
RUN pip install uv

# 复制项目代码
COPY . .

# 启动 FastAPI 服务
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]