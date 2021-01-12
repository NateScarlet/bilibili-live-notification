FROM python:3.8-alpine

# Example: https://mirrors.aliyun.com/pypi/simple
ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# Example: mirrors.tuna.tsinghua.edu.cn
ARG ALPINE_MIRROR
RUN if [ ! -z "${ALPINE_MIRROR}" ]; then \
    sed -i "s/dl-cdn.alpinelinux.org/${ALPINE_MIRROR}/g" /etc/apk/repositories && \
    cat /etc/apk/repositories; \
    fi;

RUN apk add --no-cache \
        tzdata

WORKDIR /app

COPY ./requirements.txt ./
RUN set -ex\
    && apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
    && pip install -U pip\
    && pip install -r ./requirements.txt \
    && apk del .build-deps

COPY ./ ./

ENV TZ=Asia/Shanghai
CMD [ "python3", "-m", "bilibili_live_notification" ]
