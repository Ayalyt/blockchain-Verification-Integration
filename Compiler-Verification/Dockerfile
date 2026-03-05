# Stage 1: Builder - Compiles all dependencies and binaries
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

ENV APT_SOURCE_HOST="mirrors.aliyun.com"

RUN sed -i "s@\(archive\|security\).ubuntu.com@${APT_SOURCE_HOST}@g" /etc/apt/sources.list \
    && cat /etc/apt/sources.list \
    && apt-get update --fix-missing \
    # 安装 https 协议需要的依赖
    && apt-get install -y --no-install-recommends \
        ca-certificates apt-transport-https \
    # 切换成 https 协议
    && sed -i "s@http://@https://@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl wget git build-essential cmake pkg-config libssl-dev libgmp-dev \
        python3 python3-pip python3-dev python3-venv\
    && rm -rf /var/lib/apt/lists/*

    
# 2. Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.78.0
ENV PATH="/root/.cargo/bin:${PATH}"

# 3. Build and install cvc5 from source
WORKDIR /app
COPY cvc5 /app/cvc5
RUN chmod +x /app/cvc5/configure.sh
WORKDIR /app/cvc5
RUN ./configure.sh --python-bindings --cocoa --auto-download --gpl
WORKDIR /app/cvc5/build
RUN make -j$(nproc) && \
    make install
WORKDIR /
RUN rm -rf /build

# # 4. Build the application's Rust component
# WORKDIR /app
# COPY ./RAW/AstBuiler ./RAW/AstBuiler
# RUN cd RAW/AstBuiler && cargo build --release

# 5. Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r /app/requirements.txt

# Stage 2: Final - Creates the lean production image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 1. Install only runtime dependencies
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libgmp-dev \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy installed cvc5 and its python bindings from the builder stage
COPY --from=builder /usr/local/lib/ /usr/local/lib/
COPY --from=builder /usr/local/bin/cvc5 /usr/local/bin/cvc5
COPY --from=builder /usr/local/include/cvc5 /usr/local/include/cvc5
# Note: The python version in ubuntu:22.04 is 3.10. This path is specific to it.
COPY --from=builder /usr/local/lib/python3.10/dist-packages/cvc5* /usr/local/lib/python3.10/dist-packages/

# 3. Copy other installed python packages from builder
COPY --from=builder /usr/local/lib/python3.10/dist-packages/ /usr/local/lib/python3.10/dist-packages/

# # 4. Copy the compiled Rust binary
# # The application seems to expect it in this specific 'dependence' folder.
# COPY --from=builder /app/RAW/AstBuiler/target/release/AstBuilder /app/RAW/Verifier/dependence/

# 5. Copy the application source code
COPY . .

WORKDIR /app/Compiler-Verification
