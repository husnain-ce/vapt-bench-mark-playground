FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /bot
COPY requirements.txt /bot/requirements.txt
RUN pip install --no-cache-dir -r /bot/requirements.txt     && playwright install --with-deps chromium
COPY bot.py /bot/bot.py
CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "9000"]
