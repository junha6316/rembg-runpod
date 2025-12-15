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


def download_image(url):
    """Download image from URL"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


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
        "return_base64": true  # optional, default: true
    }

    Output format:
    {
        "image_base64": "base64_encoded_image_data",
        "format": "PNG"
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
        input_image = download_image(request.image_url)

        # Remove background using BiRefNet-HRSOD
        print('get session')
        output_image = remove(input_image, session=session)
        print('remove success')

        print('return image')
        # Convert to base64 if requested
        if request.return_base64:
            image_base64 = image_to_base64(output_image)
            return {
                "image_base64": image_base64,
                "format": "PNG"
            }
        else:
            # Save to bytes and return
            buffered = BytesIO()
            output_image.save(buffered, format="PNG")
            return {
                "image_bytes": buffered.getvalue(),
                "format": "PNG"
            }

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
