# Use slim Python image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates ./templates
COPY static ./static

# Expose port for Flask
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
