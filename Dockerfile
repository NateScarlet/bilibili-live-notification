FROM python:3.8-alpine

# Example: https://mirrors.aliyun.com/pypi/simple
ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# Example: https://mirrors.tuna.tsinghua.edu.cn/alpine
ARG ALPINE_MIRROR
RUN if [ -n "${ALPINE_MIRROR}" ]; then \
    sed -i "s@https://dl-cdn.alpinelinux.org/alpine@${ALPINE_MIRROR}@g" /etc/apk/repositories && \
    cat /etc/apk/repositories; \
    fi;


WORKDIR /app

COPY ./requirements.txt ./
RUN set -ex\
    && apk add --no-cache --virtual .build-deps \
        gcc \
        g++ \
        musl-dev \
    && pip install -U pip\
    && pip install -r ./requirements.txt \
    && apk del .build-deps \
    && apk add --no-cache \
        libstdc++ 

COPY ./ ./

# https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
ENV TZ=CST-8
CMD [ "python3", "-m", "bilibili_live_notification" ]
