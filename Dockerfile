FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /mysocial_api

WORKDIR /mysocial_api

COPY . /mysocial_api

RUN pip install -r requirements.txt
