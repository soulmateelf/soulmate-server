# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 将工作目录设置为项目文件夹
WORKDIR ./soulmate_server

# 复制项目文件到容器中
COPY . .

# 安装 poetry
RUN pip install poetry

# 使用 poetry 安装项目依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# 设置默认的启动命令
CMD ["poetry","run","app"]
