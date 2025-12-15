# Use RunPod's official PyTorch GPU image
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies including cuDNN
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libcudnn8 \
    libcudnn8-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Install onnxruntime-gpu for CUDA 11.8 from special repository
RUN pip install --no-cache-dir numpy\<2.0.0 requests Pillow runpod
RUN pip install --no-cache-dir onnxruntime-gpu==1.18.1 --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-11/pypi/simple/
RUN pip install --no-cache-dir rembg

# Create model cache directory and download BiRefNet-HRSOD model into the image
# This ensures fast cold starts even without persistent volume
RUN mkdir -p /app/models
ENV U2NET_HOME=/app/models

# Copy handler code
COPY handler.py .

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
