FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Verify requirements.txt is readable
RUN cat requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install requests explicitly first to verify it works
RUN pip install --no-cache-dir requests==2.31.0

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify requests is installed and importable
RUN python -c "import requests; print(f'✓ requests {requests.__version__} installed successfully')"

# Copy application code
COPY . .

# Create directory for database (if needed)
RUN mkdir -p /app/data

# Run the bot
CMD ["python", "bot.py"]

