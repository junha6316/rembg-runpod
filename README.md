# Rembg RunPod Serverless API

RunPod Serverless API for background removal using rembg with BiRefNet-HRSOD model.

## Features

- Remove background from images using BiRefNet-HRSOD model
- GPU-accelerated processing
- Accepts image URLs
- Returns base64 encoded PNG images
- Fast cold start with pre-downloaded model

## Deployment

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t your-dockerhub-username/rembg-runpod:latest .

# Push to Docker Hub
docker push your-dockerhub-username/rembg-runpod:latest
```

### 2. Deploy to RunPod

1. Go to [RunPod Serverless](https://www.runpod.io/console/serverless)
2. Click "New Endpoint"
3. Configure:
   - **Container Image**: `your-dockerhub-username/rembg-runpod:latest`
   - **GPU Type**: Select GPU (recommended: RTX 3090 or better)
   - **Workers**: Configure auto-scaling as needed
4. Deploy

## API Usage

### Request Format

```json
{
  "input": {
    "image_url": "https://example.com/image.jpg",
    "return_base64": true
  }
}
```

### Parameters

- `image_url` (required): URL of the image to process
- `return_base64` (optional): Return base64 encoded image, default: true

### Response Format

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "format": "PNG"
}
```

### Example with Python

```python
import requests
import base64
from PIL import Image
from io import BytesIO

# Your RunPod endpoint URL
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/{your-endpoint-id}/runsync"
API_KEY = "your-api-key"

def remove_background(image_url):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "image_url": image_url
        }
    }

    response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers)
    result = response.json()

    # Decode base64 image
    image_data = base64.b64decode(result["output"]["image_base64"])
    image = Image.open(BytesIO(image_data))

    return image

# Usage
image_url = "https://example.com/photo.jpg"
result_image = remove_background(image_url)
result_image.save("output.png")
```

### Example with cURL

```bash
curl -X POST "https://api.runpod.ai/v2/{your-endpoint-id}/runsync" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image_url": "https://example.com/image.jpg"
    }
  }'
```

## Local Testing

```bash
# Build the image
docker build -t rembg-runpod .

# Run locally
docker run --gpus all -p 8000:8000 rembg-runpod

# Test the handler
python -c "
from handler import handler
result = handler({
    'input': {
        'image_url': 'https://example.com/image.jpg'
    }
})
print(result)
"
```

## Model Information

This API uses **BiRefNet-HRSOD** (Bilateral Reference Network - High-Resolution Salient Object Detection), which provides:
- High-quality background removal
- Better edge detection
- Improved handling of complex backgrounds
- Fast inference on GPU

## Error Handling

The API returns error messages in the following format:

```json
{
  "error": "Error description"
}
```

Common errors:
- `image_url is required in input`: Missing image_url parameter
- `Failed to download image`: Invalid URL or network error
- `Error processing image`: Processing error

## Performance

- Cold start: ~10-20 seconds (model pre-downloaded in image)
- Warm inference: ~1-3 seconds per image (depends on image size and GPU)
- Recommended GPU: RTX 3090 or higher

## License

This project uses the following open-source libraries:
- [rembg](https://github.com/danielgatis/rembg) - MIT License
- [RunPod](https://www.runpod.io/) - Check RunPod's terms of service
