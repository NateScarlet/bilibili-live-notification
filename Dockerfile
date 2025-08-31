FROM python:3.12-alpine

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
        libxml2-dev \
        libxslt-dev \
        jpeg-dev \
        zlib-dev \
    && pip install --root-user-action ignore -U pip 'Setuptools<81'\
    && pip install --root-user-action ignore -r ./requirements.txt \
    && apk del .build-deps \
    && apk add --no-cache \
        libstdc++ 

COPY ./ ./

# https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
ENV TZ=CST-8
CMD [ "python3", "-m", "bilibili_live_notification" ]
