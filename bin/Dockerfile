FROM python:3.8-slim
RUN apt-get update
RUN apt-get -y install curl
RUN curl -sL https://deb.nodesource.com/setup_13.x | bash
RUN apt-get -y install nodejs
RUN pip3 install awscli
WORKDIR /cdk
COPY . /cdk