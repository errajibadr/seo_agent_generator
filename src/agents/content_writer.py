"""Content writer agent for generating blog articles."""

import datetime
import json
import random
import re
from typing import List, Optional

from src.config import get_config
from src.data.models import BlogArticle, ImageDetail, KeywordData
from src.prompts.blog_post_prompt import blog_post_prompt
from src.services.openrouter_service import OpenRouterService
from src.utils.logger import get_logger
from src.utils.text_utils import estimate_reading_time, slugify

logger = get_logger(__name__)


class ContentWriter:
    """Agent for generating blog content."""

    def __init__(
        self,
        openrouter_service: Optional[OpenRouterService] = None,
        near_me: Optional[str] = None,
        prompt_template: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize the content writer agent.

        Args:
            openrouter_service: Optional service for OpenRouter API
            near_me: Optional location for local SEO
            prompt_template: Optional custom prompt template (defaults to blog_post_prompt)
            system_prompt: Optional custom system prompt
            generation_params: Optional parameters for content generation (temperature, max_tokens, etc.)
        """
        self.service = openrouter_service or OpenRouterService()
        self.config = get_config()
        self.near_me = near_me
        self.prompt_template = prompt_template or blog_post_prompt
        self.system_prompt = system_prompt or (
            "You are a professional SEO content writer. Create high-quality, "
            "SEO-optimized blog content based on the provided instructions and keywords. "
            "The output must be in valid JSON format following the structure specified in the prompt. "
            "current date is {current_date}"
        )

    def cluster_to_prompt_context(self, cluster_name: str, cluster_data: List[KeywordData]) -> dict:
        """Convert cluster data to prompt context.

        Args:
            cluster_name: Cluster name
            cluster_data: Cluster data
        """
        prompt_context = {
            "cluster_name": cluster_name,
            "keywords": [keyword_data.to_prompt_context() for keyword_data in cluster_data],
        }
        return prompt_context

    async def generate_blog(
        self, cluster_name: str, cluster_data: List[KeywordData]
    ) -> BlogArticle:
        """Generate a blog article based on keyword data.

        Args:
            keyword_data: Keyword data

        Returns:
            Generated blog article
        """
        # Format the prompt with keyword data
        prompt_context = self.cluster_to_prompt_context(cluster_name, cluster_data)
        formatted_prompt = self.prompt_template.replace(
            "{keywords}", json.dumps(prompt_context, ensure_ascii=False)
        )
        if self.near_me:
            formatted_prompt = formatted_prompt.replace("{NearMe}", self.near_me)
        else:
            formatted_prompt = formatted_prompt.replace("{NearMe}", "Not specified")

        # Format system prompt
        formatted_system_prompt = self.system_prompt.format(
            current_date=datetime.datetime.now().strftime("%Y-%m-%d")
        )

        logger.info(f"Generating blog for cluster: {cluster_name}")
        content = await self.service.generate_content(
            prompt=formatted_prompt, system_prompt=formatted_system_prompt
        )

        # Extract JSON content
        blog_json = await self.service.extract_json_from_response(content)

        if not blog_json:
            logger.error("Failed to extract JSON from response")
            logger.debug(f"Response content: {content}")
            raise ValueError("Invalid response format from AI service")

        # Extract image details from content
        image_details = self._extract_image_details(blog_json.get("Contenu article", ""))

        # Estimate reading time from content
        content_html = blog_json.get("Contenu article", "")
        reading_time = f"{estimate_reading_time(content_html)} minutes"

        # Create blog article
        return BlogArticle(
            title=blog_json.get("Titre", ""),
            slug=slugify(blog_json.get("Titre", "")),
            publication_date=(
                datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 90))
            ).strftime("%d/%m/%Y"),
            reading_time=reading_time,
            table_of_contents=blog_json.get("Table des matières", ""),
            content=content_html,
            article_type=blog_json.get("Type d'article", ""),
            article_types_secondary=blog_json.get("Type d'article 2-8", "").split(", "),
            article_summary=blog_json.get("Résumé de l'article", ""),
            title_tag=blog_json.get("Balise title", ""),
            meta_description=blog_json.get("META DESCRIPTION", ""),
            image_details=image_details,
            cluster_keyword_data=cluster_data,
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
            img_tag = match.group(0)
            alt_text = match.group(1)

            # Check if there's a placeholder in the src attribute
            placeholder = None
            placeholder_match = re.search(
                r'src="(?:{{)?([^{}]+?)(?:}})?(?:\.(jpg|png|webp))?(?:\?[^"]*)?(?:")', img_tag
            )

            if placeholder_match:
                placeholder = placeholder_match.group(1)

            # Create an image detail
            image_details.append(
                ImageDetail(
                    alt_text=alt_text,
                    description=f"Generate an image for: {alt_text}",
                    placeholder=placeholder,
                )
            )

        logger.info(f"Extracted {len(image_details)} image details from content")
        return image_details
