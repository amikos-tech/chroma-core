FROM python:3.10-slim-bookworm as builder
ARG REPO=https://github.com/chroma-core/chroma
ARG BRANCH=main
RUN apt-get update --fix-missing && apt-get install -y --fix-missing \
    build-essential \
    gcc \
    git \
    g++ && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /install && mkdir /chroma-repo
WORKDIR /chroma-repo

RUN git clone --branch ${BRANCH} ${REPO}.git .
WORKDIR /install

RUN pip install --no-cache-dir --upgrade --prefix="/install" -r /chroma-repo/requirements.txt

FROM python:3.10-slim-bookworm as final

RUN apt-get update --fix-missing && apt-get install -y --fix-missing \
    build-essential \
    gcc \
    g++ && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /chroma
WORKDIR /chroma

COPY --from=builder /install /usr/local
COPY --from=builder /chroma-repo /chroma/
COPY --from=builder /chroma-repo/bin/docker_entrypoint.sh /docker_entrypoint.sh

EXPOSE 8000

CMD ["/docker_entrypoint.sh"]