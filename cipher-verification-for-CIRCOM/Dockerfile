FROM ubuntu:24.04


SHELL ["/bin/bash", "-l", "-c"]

ENV APT_SOURCE_HOST="mirrors.aliyun.com"

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN sed -i "s@\(archive\|security\).ubuntu.com@${APT_SOURCE_HOST}@g" /etc/apt/sources.list.d/ubuntu.sources && \
    apt-get clean && \
    apt update && \
    apt upgrade -y && \
    apt install -y --fix-broken --option Acquire::Retries=999  build-essential curl git bc nano cmake gdb python3 sudo \
                   pkg-config ocaml ocaml-dune libzarith-ocaml-dev \
                   liblwt-ocaml-dev libppx-optcomp-ocaml-dev camlidl \
                   libgmp-dev libmpfr-dev libppl-dev libglpk-dev libflint-dev \
                   libbigarray-compat-ocaml-dev libreadline-dev \
                   python3-pip python3-venv libmpc-dev vim tmux z3 \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv $VIRTUAL_ENV

WORKDIR /build

RUN git clone https://github.com/berkeley-abc/abc.git abc \
    && git clone https://github.com/nberth/mlgmpidl.git mlgmpidl \
    && git clone https://github.com/antoinemine/apron.git apron \
    && git clone https://github.com/fmlab-iis/cryptoline.git cryptoline \
# Install abc -> /usr/bin
    && pushd abc \
    && make && install -m 755 -s abc /usr/bin/ \
    && popd \
# Install mlgmpidl -> /usr/local
    && pushd mlgmpidl \
    && git checkout 1.3.0 && ./configure && make && make install \
    && popd \
# Install apron -> /usr/local
    && pushd apron \
    && ./configure && make && make install \
    && popd \
# Install CryptoLine -> /usr/local
    && pushd cryptoline \
    && echo "export OCAMLPATH=`ocamlfind query apron`/.." >> ~/.bashrc \
    && export OCAMLPATH=`ocamlfind query apron`/.. \
    && mkdir -p $OCAMLPATH/camlidl/caml \
    && cp `ocamlc -where`/com.* $OCAMLPATH/camlidl/ \
    && cp `ocamlc -where`/libcamlidl.a $OCAMLPATH/camlidl/ \
    && cp `ocamlc -where`/caml/camlidlruntime.h $OCAMLPATH/camlidl/caml/ \
    && cp `ocamlc -where`/METAS/META.camlidl $OCAMLPATH/camlidl/META \
    && export OCAMLPATH=`ocamlfind query apron`/.. \
    && dune build && dune install --prefix /usr/local

WORKDIR /build/cryptoline
RUN ./scripts/install-boolector.sh \
    && ./scripts/install-singular.sh \
    && pip3 install islpy pplpy pyscipopt

RUN git clone https://github.com/cvc5/cvc5.git /build/cvc5 && \
    cd /build/cvc5 && \
    ./configure.sh --python-bindings --cocoa --auto-download --gpl && \
    cd build && \
    make -j$(nproc) && \
    make check && \
    make install

RUN rm -rf /build

WORKDIR /app

ENV OCAMLPATH="/usr/local/lib/ocaml/4.14.2/site-lib/.."

CMD ["tail", "-f", "/dev/null"]