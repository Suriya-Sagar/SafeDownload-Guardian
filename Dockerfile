# Use Python 3.10
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    procps \
    libmagic1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py ./
COPY templates/ ./templates/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p uploads uploads/extracted && \
    chmod -R 777 uploads

# Create .env file if it doesn't exist
RUN touch .env

EXPOSE 5000

CMD ["python", "app.py"]