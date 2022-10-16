FROM python:3.10

LABEL teabe service

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore

RUN mkdir -p /var/www/html/teabe

# 設定工作目錄
WORKDIR /var/www/html/teabe

# 當前目錄文件 加入工作目錄
COPY requirements.txt /var/www/html/teabe/requirements.txt

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
