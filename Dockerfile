FROM python:3.8-slim

ARG PIP_MIRROR
ENV PIP_INDEX_URL=${PIP_MIRROR}
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -U pip &&\
    pip install -r ./requirements.txt

COPY ./ ./

ENV TZ=Asia/Shanghai
CMD [ "python3", "-m", "bilibili_live_notification" ]
