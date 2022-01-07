FROM python:latest

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt