FROM alpine:3.21

WORKDIR /usr/app
COPY ./src/ .
RUN apk add --update --no-cache         \
        python3~=3                      \
        py3-pip~=24                  && \
    pip install                         \
      --no-cache-dir                    \
      --break-system-packages           \
      -r requirements.txt

USER guest
CMD ["/usr/bin/python3", "/usr/app/app.py"]
