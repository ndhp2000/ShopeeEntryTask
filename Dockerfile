FROM python:3.6.14-alpine

RUN apk update && apk add --no-cache --virtual bash gcc musl-dev linux-headers jpeg-dev zlib-dev mariadb-dev libffi-dev

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./EventManager /app
WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh","/entrypoint.sh"]