# Use an official NVIDIA CUDA runtime base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python 3.10 and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    libgl1-mesa-glx libomp-dev build-essential \
    && ln -sf python3.10 /usr/bin/python \
    && ln -sf pip3 /usr/bin/pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy the application code
COPY . .

EXPOSE 8000

# Start the Flask app
CMD ["python", "app.py"]
