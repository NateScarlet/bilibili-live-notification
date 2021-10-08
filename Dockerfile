FROM python:3.8

# Example: https://mirrors.aliyun.com/pypi/simple
ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# Example: http://mirrors.huaweicloud.com/ubuntu
ARG UBUNTU_MIRROR
RUN if [ -n "$UBUNTU_MIRROR" ]; then \
    sed -i "s@http://.\+\.ubuntu\.com/ubuntu@$UBUNTU_MIRROR@g" /etc/apt/sources.list && \
    cat /etc/apt/sources.list; \
    fi

WORKDIR /app

COPY ./requirements.txt ./
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates\
    && pip install -U pip\
    && pip install -r ./requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY ./ ./

# https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
ENV TZ=CST-8
CMD [ "python3", "-m", "bilibili_live_notification" ]
