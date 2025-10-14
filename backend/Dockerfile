# Use an official NVIDIA CUDA runtime base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install Python 3.10, pip and other necessary libs
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip python3-venv \
    libgl1-mesa-glx libomp-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to cache this step if unchanged
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt

# Copy the rest of your app code
COPY . .

# Expose the port your app will run on
EXPOSE 8000

# Command to run your app
CMD ["python3", "app.py"]

