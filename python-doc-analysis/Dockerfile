FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with retry
RUN for i in 1 2 3; do apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* && break || sleep 10; done

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 3 -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.doc_analysis.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
