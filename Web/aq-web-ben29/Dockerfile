FROM python:3.13.3-alpine

WORKDIR /app

RUN apk update && apk add build-base && rm -rf /var/cache/apk/*
RUN pip install --no-cache-dir flask gunicorn

COPY app.py /app/

RUN chmod 444 /app/app.py && \
    chmod 555 /app && \
    chown -R root:root /app

RUN echo "flag{fake}" > /flag
RUN chmod 0400 /flag
COPY readflag.c /readflag.c
RUN gcc /readflag.c -o /readflag
RUN chmod 4755 /readflag

USER nobody

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
