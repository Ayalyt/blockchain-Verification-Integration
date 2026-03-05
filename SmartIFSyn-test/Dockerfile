FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

ENV APT_SOURCE_HOST="mirrors.aliyun.com"

RUN sed -i "s@\(archive\|security\).ubuntu.com@${APT_SOURCE_HOST}@g" /etc/apt/sources.list \
    && apt-get clean \
    && apt update \
    && apt upgrade -y \
    && cat /etc/apt/sources.list \
    && apt-get update --fix-missing\
    && apt install -y --fix-broken --option Acquire::Retries=999 \
        curl wget git build-essential python3 python3-pip python3-dev python3-venv \
        sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN solc-select install 0.4.26 && solc-select use 0.4.26

RUN ln -sf /root/.solc-select/artifacts/solc-0.4.26/solc-0.4.26 /usr/local/bin/solc

RUN docker pull 1994huxinwen/stc:latest || echo "对比工具镜像拉取失败，请在运行时手动拉取"

RUN docker images | grep 1994huxinwen/stc || echo "对比工具镜像未找到"

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ENV APT_SOURCE_HOST="mirrors.aliyun.com" 

WORKDIR /app

RUN sed -i "s@\(archive\|security\).ubuntu.com@${APT_SOURCE_HOST}@g" /etc/apt/sources.list && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    sudo \
    docker.io \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/dist-packages/ /usr/local/lib/python3.10/dist-packages/
COPY --from=builder /usr/local/bin/solc-select /usr/local/bin/solc-select
COPY --from=builder /root/.solc-select /root/.solc-select

RUN ln -sf /root/.solc-select/artifacts/solc-0.4.26/solc-0.4.26 /usr/local/bin/solc

RUN echo "cache buster"
COPY . .

RUN mkdir -p /app/results

RUN echo "root ALL=(ALL) NOPASSWD: /usr/bin/docker" >> /etc/sudoers

CMD ["tail", "-f", "/dev/null"]
