FROM python:3.8.1-slim-buster

RUN apt-get update \
    && apt-get install dos2unix -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN mkdir /opt/app
COPY . /opt/app/

WORKDIR /opt/app
RUN pip install -r req-prd.txt \
    && dos2unix start-server.sh \
    && chmod +x start-server.sh

EXPOSE 8000
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]
