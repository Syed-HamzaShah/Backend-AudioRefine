FROM python:3.10-slim

# Prevent .pyc files and force unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install only necessary system packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .

# Use fixed versions to avoid bloat, but no need to pin pip/wheel unless needed
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code into the container
COPY . .

# Expose port for Render
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
