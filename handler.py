import runpod
import requests
from io import BytesIO
from PIL import Image
import base64
from rembg import remove, new_session


# Initialize BiRefNet-HRSOD session globally
session = new_session("birefnet-hrsod")


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


def handler(event):
    """
    RunPod handler function for background removal

    Input format:
    {
        "input": {
            "image_url": "https://example.com/image.jpg",
            "return_base64": true  # optional, default: true
        }
    }

    Output format:
    {
        "image_base64": "base64_encoded_image_data",
        "format": "PNG"
    }
    """
    try:
        # Extract input parameters
        input_data = event.get("input", {})
        image_url = input_data.get("image_url")
        return_base64 = input_data.get("return_base64", True)

        if not image_url:
            return {
                "error": "image_url is required in input"
            }

        # Download image from URL
        input_image = download_image(image_url)

        # Remove background using BiRefNet-HRSOD
        output_image = remove(input_image, session=session)

        # Convert to base64 if requested
        if return_base64:
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
    runpod.serverless.start({"handler": handler})
