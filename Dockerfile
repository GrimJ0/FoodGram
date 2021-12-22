FROM python:3.9.6-alpine

ENV APP_HOME=/code

RUN mkdir $APP_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $APP_HOME

RUN mkdir $APP_HOME/static_cdn
RUN mkdir $APP_HOME/media

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && apk del build-deps

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r /$APP_HOME/requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /$APP_HOME/entrypoint.sh
RUN chmod +x /$APP_HOME/entrypoint.sh

COPY . .

ENTRYPOINT ["/code/entrypoint.sh"]