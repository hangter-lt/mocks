# 使用Ubuntu 22.04作为基础镜像，它的GLIBC版本是2.35
FROM ubuntu:22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive

# 更新apt源并安装必要的软件包
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 创建应用程序目录
WORKDIR /app

# 首先创建一个空的虚拟环境目录
RUN mkdir -p venv

# 复制requirements.txt文件和run.py文件（仅复制必要的文件，避免复制本地的venv目录）
COPY requirements.txt .
COPY run.py .

# 创建虚拟环境并安装依赖（这将在容器内部创建一个全新的虚拟环境）
RUN python3.11 -m venv venv \
    && ./venv/bin/pip install --upgrade pip \
    && ./venv/bin/pip install -r requirements.txt \
    && echo "验证gunicorn安装：" && ./venv/bin/pip show gunicorn

# 复制应用程序代码（在创建虚拟环境后复制，避免覆盖）
# 使用.dockerignore文件排除venv目录和其他不需要的文件
COPY app/ ./app/

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动应用程序 - 使用Python执行gunicorn模块
CMD ["./venv/bin/python3", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "run:app"]