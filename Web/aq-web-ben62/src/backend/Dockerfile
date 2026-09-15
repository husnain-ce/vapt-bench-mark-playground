FROM alpine:3.20.3

WORKDIR /usr/app
COPY ./api/ .
COPY ./haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg

RUN apk add --update --no-cache tzdata python3 py3-pip haproxy \
    && pip install --no-cache-dir --break-system-packages -r requirements.txt

CMD ["sh", "-c", "haproxy -f /etc/haproxy/haproxy.cfg & python api.py"]
