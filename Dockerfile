# Use RunPod's official PyTorch GPU image
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download BiRefNet-HRSOD model during build to reduce cold start time
RUN python -c "from rembg import new_session; new_session('birefnet-hrsod')"

# Copy handler code
COPY handler.py .

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
