FROM debian:bullseye-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bash \
        build-essential \
        ca-certificates \
        curl \
        firefox-esr \
        git \
        libbz2-dev \
        libffi-dev \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        liblzma-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libtiff5-dev \
        libxml2-dev \
        libxslt1-dev \
        tk-dev \
        uuid-dev \
        wget \
        xvfb \
        xz-utils \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*
