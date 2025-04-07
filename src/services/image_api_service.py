"""Image API service for generating images."""

import base64
import io
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ImageAPIService:
    """Service for interacting with image generation APIs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the image API service.

        Args:
            api_key: API key for image generation service (defaults to config value)
            base_url: Base URL for image API (defaults to config value)
            output_dir: Directory to save generated images (defaults to output/images)
        """
        config = get_config()
        self.api_key = api_key or config.api.image_api_key
        self.gemini_api_key = config.api.gemini_api_key
        # Update the base URL for the direct Gemini API
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = config.api.http_timeout
        self.output_dir = output_dir if output_dir else Path("output/images")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.api_key and not self.gemini_api_key:
            raise ValueError("Image API key is required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _make_api_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> list[Dict[str, Any]]:
        """Make an API request to the image service.

        Args:
            endpoint: API endpoint
            payload: Request payload
            headers: Optional request headers

        Returns:
            API response
        """
        # Construct the URL with API key as query parameter
        url = f"{self.base_url}/{endpoint}?key={self.gemini_api_key or self.api_key}"

        default_headers = {
            "Content-Type": "application/json",
        }

        # Merge default headers with any provided headers
        request_headers = {**default_headers, **(headers or {})}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=request_headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Handle rate limiting
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", "5"))
                logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                raise
            raise
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise

    async def generate_image(
        self,
        prompt: str,
        placeholder: str | None = None,
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None,
    ) -> str:
        """Generate an image using the image generation API.

        Args:
            prompt: Text description of the image to generate
            width: Image width
            height: Image height
            style: Optional style parameter

        Returns:
            URL of the generated image as a string
        """
        logger.info(f"Generating image with prompt: {prompt[:50]}...")

        try:
            # Prepare the request payload for the Gemini model
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseModalities": ["image", "text"],
                    "responseMimeType": "text/plain",
                },
            }

            # Add style if provided
            if style:
                payload["generationConfig"]["style"] = style

            # Make the API request to generate content
            model_id = "gemini-2.0-flash-exp-image-generation"
            endpoint = f"models/{model_id}:streamGenerateContent"

            response = await self._make_api_request(endpoint, payload)

            if isinstance(response, list):
                response = response[0]

            # Process the response to extract image data
            if not response or "candidates" not in response or not response["candidates"]:
                raise ValueError("No valid response from API")

            candidate = response["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                raise ValueError("Invalid response format")

            # Find the image part in the response
            image_data = None
            for part in candidate["content"]["parts"]:
                if "inlineData" in part and part["inlineData"]["mimeType"].startswith("image/"):
                    image_data = base64.b64decode(part["inlineData"]["data"])
                    break

            if not image_data:
                raise ValueError("No image data found in response")

            # Generate a unique filename with WebP format for better compression
            filename = f"{placeholder}_{str(uuid.uuid4())[:8]}.webp".lstrip("_")
            filepath = self.output_dir / filename

            # Convert image data to WebP format for better compression

            # Create an image from the binary data
            img = Image.open(io.BytesIO(image_data))

            # Save as WebP with high quality but good compression
            img.save(filepath, format="WEBP", quality=85, method=6)

            # Return the file URL
            image_url = f"{str(self.output_dir)}/{filename}"

            logger.info(f"Image generated and saved to: {filepath}")
            return image_url

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise


# Add a main function for testing
async def main():
    service = ImageAPIService()
    await service.generate_image(
        placeholder="Éducateur canin travaillant",
        prompt="Generate an image for: Éducateur canin travaillant...",
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
