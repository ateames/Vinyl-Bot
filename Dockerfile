# Use a lightweight Python image (ensure this image is ARM-compatible for your Raspberry Pi)
FROM python:3.9-slim

# Set noninteractive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install system dependencies for PyAudio and building Python packages
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . /app

# Expose port 5000 for the Flask application
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
