FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_HOME=/opt/cargo
ENV CARGO_TARGET_DIR=/opt/cargo-target
ENV PATH="/opt/cargo/bin:${PATH}"

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    pkg-config \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*
    

RUN apt-get update && apt-get install -y \
    nasm \
    libssl-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*
    
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    rm -rf /var/lib/apt/lists/*

ARG RUST_TOOLCHAIN="nightly-2025-05-30"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain ${RUST_TOOLCHAIN} || \
    (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly)

RUN rustup component add llvm-tools-preview

RUN curl -L https://github.com/mozilla/grcov/releases/latest/download/grcov-x86_64-unknown-linux-gnu.tar.bz2 | \
    tar jxf - -C /usr/local/bin

WORKDIR /app

COPY . .

RUN if [ -d "assets/circom-202" ]; then \
      cd assets/circom-202 && \
      cargo fetch && \
      cargo build --release && \
      cp /opt/cargo-target/release/circom-202 /usr/local/bin/ && \
      mkdir -p target/release && \
      cp /opt/cargo-target/release/circom-202 target/release/ 2>/dev/null || true; \
    fi && \
    if [ -d "assets/circom-218" ]; then \
      cd assets/circom-218 && \
      cargo fetch && \
      cargo build --release && \
      cp /opt/cargo-target/release/circom-218 /usr/local/bin/ && \
      mkdir -p target/release && \
      cp /opt/cargo-target/release/circom-218 target/release/ 2>/dev/null || true; \
    fi


RUN mkdir -p /opt/node_cache/cmd /opt/node_cache/lib/snarkjs

RUN if [ -d "cmd" ]; then \
      cd cmd && CI=true pnpm install && mv node_modules /opt/node_cache/cmd/; \
    fi

RUN if [ -d "lib/snarkjs" ]; then \
      cd lib/snarkjs && CI=true pnpm install && mv node_modules /opt/node_cache/lib/snarkjs/; \
    fi

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN chmod +x /app/cases/*.sh 2>/dev/null || true
RUN chmod +x -R /app 2>/dev/null || true

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
