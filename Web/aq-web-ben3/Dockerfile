# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for xmlsec and lxml
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxml2 \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create saml directory if it doesn't exist
RUN mkdir -p saml

# Generate self-signed certificates for development (optional)
# In production, mount your own certificates as volumes
RUN openssl req -x509 -newkey rsa:2048 -keyout saml/sp.key -out saml/sp.crt \
    -days 365 -nodes -subj "/CN=localhost" || true

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
