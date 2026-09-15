FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install && \
    playwright install-deps

# Install playwright browsers
RUN python -m playwright install chromium

# Copy bot code
COPY . .

EXPOSE 8000

ENV WEB_HOST=web
ENV WEB_PORT=5000
ENV INTERVAL=10

CMD ["python", "bot.py"]
