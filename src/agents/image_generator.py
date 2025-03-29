"""Image generator agent for creating images based on descriptions."""

import asyncio
import re
from typing import Dict, List, Optional, Tuple

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

        # Replace image placeholders in content with actual URLs
        blog_article.content = self._replace_image_placeholders(blog_article)

        return blog_article

    def _replace_image_placeholders(self, blog_article: BlogArticle) -> str:
        """Replace image placeholders in blog content with generated image URLs.

        Args:
            blog_article: Blog article with image details and content

        Returns:
            Updated blog content with actual image URLs
        """
        content = blog_article.content

        # Create mappings for image lookup by alt text and placeholder
        alt_to_image, placeholder_to_image = self._create_image_mappings(blog_article.image_details)

        # First try replacing direct placeholder patterns like {{placeholder_name}}
        content = self._replace_placeholder_patterns(content, placeholder_to_image)

        # Then fall back to replacing img tags based on alt text
        content = self._replace_img_tags(content, alt_to_image)

        return content

    def _create_image_mappings(
        self, image_details: List[ImageDetail]
    ) -> Tuple[Dict[str, ImageDetail], Dict[str, ImageDetail]]:
        """Create mappings from alt text and placeholders to image details.

        Args:
            image_details: List of image detail objects

        Returns:
            Tuple of (alt_to_image, placeholder_to_image) dictionaries
        """
        # Map from alt text to image details
        alt_to_image: Dict[str, ImageDetail] = {
            img.alt_text: img for img in image_details if img.url
        }

        # Map from placeholder to image details
        placeholder_to_image: Dict[str, ImageDetail] = {
            img.placeholder: img for img in image_details if img.placeholder and img.url
        }

        return alt_to_image, placeholder_to_image

    def _replace_placeholder_patterns(
        self, content: str, placeholder_to_image: Dict[str, ImageDetail]
    ) -> str:
        """Replace {{placeholder}} patterns in content with image URLs.

        Args:
            content: HTML content
            placeholder_to_image: Mapping from placeholder to image details

        Returns:
            Updated content with placeholders replaced by URLs
        """
        if not placeholder_to_image:
            return content

        updated_content = content
        for placeholder, img_detail in placeholder_to_image.items():
            if img_detail.url:  # Ensure URL is not None
                placeholder_pattern = r"{{" + re.escape(placeholder) + r"}}"
                updated_content = re.sub(placeholder_pattern, img_detail.url, updated_content)
                logger.info(f"Replaced placeholder: {placeholder} with URL: {img_detail.url}")

        return updated_content

    def _replace_img_tags(self, content: str, alt_to_image: Dict[str, ImageDetail]) -> str:
        """Replace src attributes in img tags based on matching alt text.

        Args:
            content: HTML content
            alt_to_image: Mapping from alt text to image details

        Returns:
            Updated content with img src attributes replaced
        """
        if not alt_to_image:
            logger.warning("No valid image URLs to replace in content")
            return content

        # Find all img tags with alt attribute and replace src attributes
        img_pattern = r'<img[^>]+alt="([^"]+)"[^>]*>'
        updated_content = re.sub(
            img_pattern, lambda match: self._process_img_tag(match, alt_to_image), content
        )

        # Count replaced images for logging
        replaced_count = sum(
            1 for alt in alt_to_image if re.search(f'alt="{re.escape(alt)}"', content)
        )
        logger.info(f"Replaced {replaced_count} image placeholders in content")

        return updated_content

    def _process_img_tag(self, match: re.Match, alt_to_image: Dict[str, ImageDetail]) -> str:
        """Process a single img tag match and update its attributes.

        Args:
            match: Regex match object for the img tag
            alt_to_image: Mapping from alt text to image details

        Returns:
            Updated img tag string
        """
        alt_text = match.group(1)
        img_tag = match.group(0)

        if alt_text not in alt_to_image:
            logger.warning(f"No matching image found for alt text: {alt_text}")
            return img_tag

        # Image URL found, replace or add src attribute
        img_detail = alt_to_image[alt_text]

        # Update src attribute
        if 'src="' in img_tag:
            new_img_tag = re.sub(r'src="[^"]*"', f'src="{img_detail.url}"', img_tag)
        else:
            new_img_tag = img_tag.replace(">", f' src="{img_detail.url}">')

        # Add width and height attributes if available
        # new_img_tag = self._update_img_dimensions(new_img_tag, img_detail)

        logger.info(f"Replaced image placeholder for: {alt_text}")
        return new_img_tag

    def _update_img_dimensions(self, img_tag: str, img_detail: ImageDetail) -> str:
        """Update width and height attributes of an img tag.

        Args:
            img_tag: HTML img tag string
            img_detail: Image detail with width and height

        Returns:
            Updated img tag string with width and height attributes
        """
        if not (img_detail.width and img_detail.height):
            return img_tag

        new_img_tag = img_tag

        # Add width attribute
        if 'width="' in new_img_tag:
            new_img_tag = re.sub(r'width="[^"]*"', f'width="{img_detail.width}"', new_img_tag)
        else:
            new_img_tag = new_img_tag.replace(">", f' width="{img_detail.width}">')

        # Add height attribute
        if 'height="' in new_img_tag:
            new_img_tag = re.sub(r'height="[^"]*"', f'height="{img_detail.height}"', new_img_tag)
        else:
            new_img_tag = new_img_tag.replace(">", f' height="{img_detail.height}">')

        return new_img_tag

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
                height=1024,
            )

            # Update image detail
            image_detail.url = image_url
            image_detail.width = 1024
            image_detail.height = 1024
            image_detail.generated = True

            logger.info(f"Image generated: {image_url}")

            return image_detail

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
