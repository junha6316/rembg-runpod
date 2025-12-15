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

### 2. Create Network Volume (Recommended)

Persistent volume을 사용하면 모델 파일을 캐싱하여 cold start 시간을 크게 단축할 수 있습니다.

1. Go to [RunPod Storage](https://www.runpod.io/console/serverless/user/storage)
2. Click "Create Network Volume"
3. Configure:
   - **Name**: `rembg-models` (또는 원하는 이름)
   - **Size**: 10GB 이상 권장
   - **Region**: Endpoint와 같은 region 선택
4. Create

### 3. Deploy to RunPod

1. Go to [RunPod Serverless](https://www.runpod.io/console/serverless)
2. Click "New Endpoint"
3. Configure:
   - **Container Image**: `your-dockerhub-username/rembg-runpod:latest`
   - **GPU Type**: Select GPU (recommended: RTX 3090 or better)
   - **Network Volume**: Select the volume created in step 2 (선택사항이지만 강력 권장)
   - **Workers**: Configure auto-scaling as needed
4. Deploy

**참고**: Network Volume을 연결하면:
- 첫 실행 시 모델이 `/runpod-volume/models`에 다운로드됨
- 이후 실행에서는 캐시된 모델을 재사용하여 cold start 시간 단축
- Volume 없이도 동작하지만, 매번 모델을 다운로드해야 함

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

### With Persistent Volume (Recommended)
- First cold start: ~15-25 seconds (모델 다운로드 포함)
- Subsequent cold starts: ~3-5 seconds (캐시된 모델 사용)
- Warm inference: ~1-3 seconds per image

### Without Persistent Volume
- Cold start: ~15-25 seconds (매번 모델 다운로드)
- Warm inference: ~1-3 seconds per image

**권장 사양**:
- GPU: RTX 3090 or higher
- Network Volume: 10GB+ (persistent volume 사용 시)

## License

This project uses the following open-source libraries:
- [rembg](https://github.com/danielgatis/rembg) - MIT License
- [RunPod](https://www.runpod.io/) - Check RunPod's terms of service
