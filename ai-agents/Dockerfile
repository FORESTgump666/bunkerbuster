FROM python:3.11-slim

WORKDIR /app

# Install system deps without gcc (use precompiled wheels)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python deps (gcc optional, wheels prefer)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

CMD ["python", "main.py"]

