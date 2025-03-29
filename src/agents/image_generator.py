"""Image generator agent for creating images based on descriptions."""

import asyncio
from typing import Optional

from pydantic import HttpUrl

from src.config import get_config
from src.data.models import BlogArticle, ImageDetail
from src.services.image_api_service import ImageAPIService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ImageGenerator:
    """Agent for generating images for blog articles."""

    def __init__(self, image_service: Optional[ImageAPIService] = None):
        """Initialize the image generator agent.

        Args:
            image_service: Optional service for image generation API
        """
        self.service = image_service or ImageAPIService()
        self.config = get_config()

    async def generate_images(self, blog_article: BlogArticle) -> BlogArticle:
        """Generate images for a blog article.

        Args:
            blog_article: Blog article with image details

        Returns:
            Blog article with updated image details
        """
        if not blog_article.image_details:
            logger.warning(f"No image details found for article: {blog_article.title}")
            return blog_article

        logger.info(
            f"Generating {len(blog_article.image_details)} images for article: {blog_article.title}"
        )

        # Generate images concurrently with rate limiting
        tasks = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests

        async def generate_with_semaphore(image_detail):
            async with semaphore:
                return await self._generate_single_image(image_detail)

        # Create tasks for image generation
        for image_detail in blog_article.image_details:
            task = generate_with_semaphore(image_detail)
            tasks.append(task)

        # Wait for all tasks to complete
        updated_image_details = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and update blog article
        valid_image_details = [
            detail for detail in updated_image_details if isinstance(detail, ImageDetail)
        ]

        # Count successes and failures
        successes = len(valid_image_details)
        failures = len(updated_image_details) - successes

        if failures > 0:
            logger.warning(f"Failed to generate {failures} images")

        logger.info(f"Successfully generated {successes} images")

        # Update blog article with generated images
        blog_article.image_details = valid_image_details

        return blog_article

    async def _generate_single_image(self, image_detail: ImageDetail) -> ImageDetail:
        """Generate a single image.

        Args:
            image_detail: Image detail with description

        Returns:
            Updated image detail with URL
        """
        try:
            # Generate image
            logger.info(f"Generating image: {image_detail.alt_text}")
            image_url = await self.service.generate_image(
                prompt=image_detail.description,
                width=1024,
                height=768,
            )

            # Update image detail
            image_detail.url = HttpUrl(image_url)
            image_detail.width = 1024
            image_detail.height = 768
            image_detail.generated = True

            logger.info(f"Image generated: {image_url}")

            return image_detail

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
