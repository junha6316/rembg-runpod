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

# Install dependencies in correct order to avoid numpy 2.x

# 2. Install onnxruntime-gpu for CUDA 11.8 from special repository
RUN pip install --no-cache-dir onnxruntime-gpu==1.18.1 --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-11/pypi/simple/

# 3. Install rembg dependencies manually to control versions
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    requests \
    Pillow \
    runpod \
    opencv-python-headless \
    scikit-image \
    pooch \
    tqdm \
    aiohttp \
    rembg[gpu]==2.0.50 \
    fastapi \
    uvicorn 

# Create model cache directory and download BiRefNet-HRSOD model into the image
# This ensures fast cold starts even without persistent volume
RUN mkdir -p /app/models
ENV U2NET_HOME=/app/models

# Copy handler code
COPY handler.py .

# Set the entrypoint
CMD ["python", "-u", "handler.py"]
