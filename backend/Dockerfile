# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install ffmpeg and clean up after
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Render sets PORT automatically, falling back to 8000)
EXPOSE 8000

# Command to run the application (Render injects PORT, usually 10000)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"
