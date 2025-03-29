"""Content writer agent for generating blog articles."""

import json
import re
from typing import List, Optional

from src.config import get_config
from src.data.models import BlogArticle, ImageDetail, KeywordData
from src.prompts.blog_post_prompt import blog_post_prompt
from src.services.openrouter_service import OpenRouterService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ContentWriter:
    """Agent for generating blog content."""

    def __init__(self, openrouter_service: Optional[OpenRouterService] = None):
        """Initialize the content writer agent.

        Args:
            openrouter_service: Optional service for OpenRouter API
        """
        self.service = openrouter_service or OpenRouterService()
        self.config = get_config()

    async def generate_blog(self, keyword_data: KeywordData) -> BlogArticle:
        """Generate a blog article based on keyword data.

        Args:
            keyword_data: Keyword data

        Returns:
            Generated blog article
        """
        # Format the prompt with keyword data
        prompt_context = keyword_data.to_prompt_context()
        formatted_prompt = blog_post_prompt.replace(
            "{keywords}", json.dumps(prompt_context, ensure_ascii=False)
        )

        # Generate content
        system_prompt = (
            "You are a professional SEO content writer. Create high-quality, "
            "SEO-optimized blog content based on the provided instructions and keywords. "
            "The output must be in valid JSON format following the structure specified in the prompt."
        )

        logger.info(f"Generating blog for keyword: {keyword_data.keyword}")
        content = await self.service.generate_content(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )

        # Extract JSON content
        blog_json = await self.service.extract_json_from_response(content)

        if not blog_json:
            logger.error("Failed to extract JSON from response")
            logger.debug(f"Response content: {content}")
            raise ValueError("Invalid response format from AI service")

        # Extract image details from content
        image_details = self._extract_image_details(blog_json.get("Contenu article", ""))

        # Create blog article
        return BlogArticle(
            title=blog_json.get("Titre", ""),
            slug=blog_json.get("Slug", ""),
            publication_date=blog_json.get("Date de publication", ""),
            reading_time=blog_json.get("Durée de lecture", ""),
            table_of_contents=blog_json.get("Table des matières", ""),
            content=blog_json.get("Contenu article", ""),
            article_type=blog_json.get("Type d'article", ""),
            article_types_secondary=blog_json.get("Type d'article 2-8", "").split(", "),
            article_summary=blog_json.get("Résumé de l'article", ""),
            title_tag=blog_json.get("Balise title", ""),
            meta_description=blog_json.get("META DESCRIPTION", ""),
            keyword_data=keyword_data,
            image_details=image_details,
        )

    def _extract_image_details(self, content: str) -> List[ImageDetail]:
        """Extract image details from HTML content.

        Args:
            content: HTML content

        Returns:
            List of image details
        """
        image_details = []

        # Find all img tags in content
        img_pattern = r'<img[^>]+alt="([^"]+)"[^>]*>'
        img_tags = re.finditer(img_pattern, content)

        for i, match in enumerate(img_tags):
            alt_text = match.group(1)

            # Create an image detail
            image_details.append(
                ImageDetail(
                    alt_text=alt_text,
                    description=f"Generate an image for: {alt_text}",
                )
            )

        logger.info(f"Extracted {len(image_details)} image details from content")
        return image_details
