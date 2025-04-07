FROM python:3.13-slim AS base

# Keep Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Turn off buffering for simplified logging
ENV PYTHONUNBUFFERED=1

# Install dependencies for GDAL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
FROM base AS build
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose the application port
EXPOSE 8000

# Start the application (reload is enabled for development/testing)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
