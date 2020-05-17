FROM python:3.7.7-alpine

RUN mkdir -p /opt/app/
WORKDIR /opt/app
ADD . /opt/app

### Alpine build tools and etc.
RUN apk add --no-cache git \
  && apk --update add --no-cache --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies
###
