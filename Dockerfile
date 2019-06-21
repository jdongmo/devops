FROM alpine:3.9.4

RUN apk update && \
  apk upgrade

RUN apk add --no-cache make gcc musl-dev openssl-dev openssh-client \
  python3 python3-dev libffi libffi-dev

RUN pip3 install --upgrade pip

WORKDIR /opt/devops
COPY . /opt/devops

RUN pip3 install --requirement requirements.txt

RUN apk add --no-cache vim
