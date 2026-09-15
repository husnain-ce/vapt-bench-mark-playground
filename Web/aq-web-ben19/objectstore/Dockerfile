FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8082
ENV FLASK_RUN_HOST=0.0.0.0
ADD --chmod=444 flag.txt .
RUN mkdir -p /data/FLAG && mv flag.txt /data/FLAG/flag-$(md5sum flag.txt | awk '{print $1}').txt
CMD ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:8082", "app:app"]
