"""Image API service for generating images."""

import time
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ImageAPIService:
    """Service for interacting with image generation APIs."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the image API service.

        Args:
            api_key: API key for image generation service (defaults to config value)
            base_url: Base URL for image API (defaults to config value)
        """
        config = get_config()
        self.api_key = api_key or config.api.image_api_key
        self.base_url = base_url or config.api.image_api_base_url
        self.timeout = config.api.http_timeout

        if not self.api_key:
            raise ValueError("Image API key is required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _make_api_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make an API request to the image service.

        Args:
            endpoint: API endpoint
            payload: Request payload

        Returns:
            API response
        """
        url = f"{self.base_url}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
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
        width: int = 1024,
        height: int = 768,
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
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
        }

        if style:
            payload["style"] = style

        logger.info(f"Generating image with prompt: {prompt[:50]}...")

        # In a real implementation, this would call an actual image generation API
        # For this example, we'll use a placeholder

        # Placeholder implementation (in a real app, uncomment the API call)
        # response = await self._make_api_request("images/generations", payload)
        # image_url = response["data"][0]["url"]

        # Placeholder for testing
        image_url = f"https://example.com/images/generated-{int(time.time())}.jpg"

        logger.info(f"Image generated: {image_url}")
        return image_url
