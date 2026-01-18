# Dockerfile for AI Blind Assistant
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libasound2-dev \
    libatlas-base-dev \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    bluetooth \
    bluez \
    gpsd \
    gpsd-clients \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for models and logs
RUN mkdir -p models logs

# Download models (this would be done in a separate step for production)
# RUN python scripts/download_models.py

# Expose port for web GUI
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
