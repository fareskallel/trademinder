# backend/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (can be extended later if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend source code into the container
COPY . /app

# Make sure Python can import modules from /app
ENV PYTHONPATH=/app

# Default command (used for the gateway service; overridden for others in docker-compose)
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
