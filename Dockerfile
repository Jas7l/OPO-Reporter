FROM python:3.12-slim

WORKDIR /app
RUN apt update && \
    apt install -y locales gcc python3-dev build-essential && \
    locale-gen ru_RU && locale-gen ru_RU.UTF-8 && update-locale

COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY uwsgi.ini /app/

COPY . .
WORKDIR /app/src

CMD ["uwsgi", "--ini", "../uwsgi.ini"]
