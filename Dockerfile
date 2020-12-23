FROM python:3.8

ARG PIP_MIRROR
ENV PIP_INDEX_URL=${PIP_MIRROR}
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -U pip &&\
    pip install -r ./requirements.txt

COPY ./ ./

CMD [ "python3", "-m", "bilibili_live_notification" ]
