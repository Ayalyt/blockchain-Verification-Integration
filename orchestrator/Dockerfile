FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl wget \
    && wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 3 -O /tmp/docker.tgz https://download.docker.com/linux/static/stable/x86_64/docker-20.10.9.tgz \
    && tar -xz -C /tmp -f /tmp/docker.tgz \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && rm -rf /tmp/docker* /tmp/docker.tgz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY orchestrator/docker-compose /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose

COPY orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY orchestrator/main.py .
COPY ./tools-config.yml .
