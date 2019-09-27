FROM alpine:3.9.4

RUN apk update && \
  apk upgrade

RUN apk add --no-cache make gcc musl-dev openssl-dev openssh-client \
  python3 python3-dev libffi libffi-dev vim bash && \
  ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install --upgrade pip

WORKDIR /opt/devops
COPY . /opt/devops

RUN pip3 install --requirement requirements.txt

RUN adduser -S -u 1000 ansible-user

USER ansible-user
