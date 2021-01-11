FROM python:3.8-slim

ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

WORKDIR /app

COPY ./requirements.txt ./
RUN set -ex\
    && pip install -U pip\
    && pip install -r ./requirements.txt

COPY ./ ./

ENV TZ=Asia/Shanghai
CMD [ "python3", "-m", "bilibili_live_notification" ]
