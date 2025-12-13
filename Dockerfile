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

# Create model cache directory and download BiRefNet-HRSOD model into the image
# This ensures fast cold starts even without persistent volume
RUN mkdir -p /app/models
ENV U2NET_HOME=/app/models
RUN python -c "from rembg import new_session; session = new_session('birefnet-hrsod'); print('Model downloaded successfully')"

# Copy handler code
COPY handler.py .

# Create directory for persistent volume mount point
RUN mkdir -p /runpod-volume

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
