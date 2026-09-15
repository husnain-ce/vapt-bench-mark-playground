FROM alpine:3.20.3

WORKDIR /usr/app
COPY ./src/ .
COPY ../../flag.txt /

RUN apk add --update --no-cache python3 py3-pip \
    && pip install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["sh", "-c", "python app.py"]