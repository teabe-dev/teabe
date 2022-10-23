FROM python:3.10

LABEL teabe service

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore

RUN mkdir -p /var/www/html/teabe

WORKDIR /var/www/html/teabe

COPY requirements.txt /var/www/html/teabe/requirements.txt

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
