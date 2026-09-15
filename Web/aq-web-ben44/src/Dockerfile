FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app/ /app/app
COPY ./main.py /app/main.py

RUN chmod 777 /app
RUN chmod 555 /app/main.py
RUN rm -rf /app/Dockerfile


COPY requirements.txt /app

CMD ["python3","-u","/app/main.py"]