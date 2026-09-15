FROM python:3.13-alpine

WORKDIR /app

RUN apk update && apk add build-base && rm -rf /var/cache/apk/*
RUN pip install --no-cache-dir flask werkzeug gunicorn mercurial

# Copy application files
COPY app.py /app/
COPY templates/ /app/templates/

# Set strict permissions on application files
RUN chmod 444 /app/app.py && \
    chmod -R 444 /app/templates/ && \
    chmod 555 /app /app/templates && \
    chown -R root:root /app

# Create repos directory with proper ownership for nobody user
RUN mkdir -p /tmp/repos && \
    chown nobody:nogroup /tmp/repos && \
    chmod 755 /tmp/repos

RUN echo "flag{fake}" > /flag
RUN chmod 0400 /flag
COPY readflag.c /readflag.c
RUN gcc /readflag.c -o /readflag
RUN chmod 4755 /readflag

USER nobody

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000",  "app:app"]