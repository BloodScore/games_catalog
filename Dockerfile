# pull official base image
FROM python:3.8
# set work directory
RUN mkdir -p /usr/src/app/
RUN mkdir -p /usr/src/app/static/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt