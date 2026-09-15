#!/bin/sh
set -eu

mkdir -p /run/nightbyte /data

if [ ! -f /run/nightbyte/server.key ] || [ ! -f /run/nightbyte/server.crt ]; then
  openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout /run/nightbyte/server.key \
    -out /run/nightbyte/server.crt \
    -days 3650 \
    -subj "/CN=localhost"
fi

DISABLE_BOT=1 python -m app.seed

exec gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --threads 8 \
  --timeout 60 \
  --keyfile /run/nightbyte/server.key \
  --certfile /run/nightbyte/server.crt \
  "app:create_app()"
