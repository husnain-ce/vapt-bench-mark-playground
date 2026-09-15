FROM python@sha256:157a371e60389919fe4a72dff71ce86eaa5234f59114c23b0b346d0d02c74d39

RUN pip3 install flask gunicorn redis
COPY ./stuff/ /app/
WORKDIR /app/
CMD gunicorn -b 0.0.0.0:8080 chall:app

