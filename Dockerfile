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

# https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
ENV TZ=-8
CMD [ "python3", "-m", "bilibili_live_notification" ]
