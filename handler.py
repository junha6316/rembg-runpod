from fastapi import FastAPI
from pydantic import BaseModel
import requests
from io import BytesIO
from PIL import Image
import base64
import os
from rembg import remove, new_session
import uvicorn


# Set up model cache path
# Priority: 1) Persistent volume 2) Built-in models in image
VOLUME_PATH = ""
BUILTIN_MODEL_PATH = "/app/models"

if os.path.exists(VOLUME_PATH):
    MODEL_CACHE_PATH = os.path.join(VOLUME_PATH, "models")
    os.makedirs(MODEL_CACHE_PATH, exist_ok=True)
    os.environ["U2NET_HOME"] = MODEL_CACHE_PATH
    print(f"Using persistent volume for model cache: {MODEL_CACHE_PATH}")
else:
    # Use built-in models from Docker image
    os.environ["U2NET_HOME"] = BUILTIN_MODEL_PATH
    print(f"Using built-in model cache from image: {BUILTIN_MODEL_PATH}")



session = new_session("birefnet-hrsod")

# Initialize FastAPI app
app = FastAPI()


class RemoveBackgroundRequest(BaseModel):
    image_url: str
    return_base64: bool = True
    include_original: bool = False


def download_image(url):
    """Download image from URL and return PIL image plus raw bytes"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    content = response.content
    return Image.open(BytesIO(content)), content


def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def bytes_to_base64(data: bytes):
    """Convert raw bytes to base64 string"""
    return base64.b64encode(data).decode()


@app.get("/ping")
async def health_check():
    """Health check endpoint required for load balancing"""
    return {"status": "healthy"}


@app.post("/remove-background")
async def remove_background(request: RemoveBackgroundRequest):
    """
    Remove background from image

    Input format:
    {
        "image_url": "https://example.com/image.jpg",
        "return_base64": true,  # optional, default: true
        "include_original": false  # optional, default: false
    }

    Output format:
    {
        "image_base64": "base64_encoded_image_data",  # or image_bytes when return_base64 is false
        "format": "PNG",
        "original_image_base64": "base64_encoded_original",  # or original_image_bytes when return_base64 is false
        "original_format": "PNG"
    }
    """
    try:
        print('start removing background image')

        if not request.image_url:
            return {
                "error": "image_url is required"
            }

        print('download image')
        # Download image from URL
        input_image, original_bytes = download_image(request.image_url)
        original_format = input_image.format or "PNG"

        # Remove background using BiRefNet-HRSOD
        print('get session')
        output_image = remove(input_image, session=session)
        print('remove success')

        print('return image')
        original_payload = {}
        if request.include_original:
            if request.return_base64:
                original_payload["original_image_base64"] = bytes_to_base64(original_bytes)
            else:
                original_payload["original_image_bytes"] = original_bytes
            original_payload["original_format"] = original_format

        # Convert to base64 if requested
        if request.return_base64:
            image_base64 = image_to_base64(output_image)
            response_data = {
                "image_base64": image_base64,
                "format": "PNG"
            }
            if request.include_original:
                response_data.update(original_payload)
            return response_data
        else:
            # Save to bytes and return
            buffered = BytesIO()
            output_image.save(buffered, format="PNG")
            response_data = {
                "image_bytes": buffered.getvalue(),
                "format": "PNG"
            }
            if request.include_original:
                response_data.update(original_payload)
            return response_data

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to download image: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Error processing image: {str(e)}"
        }


if __name__ == "__main__":
    print("Starting FastAPI server for load balancing...")
    port = int(os.getenv("PORT", "80"))
    uvicorn.run(app, host="0.0.0.0", port=port)
