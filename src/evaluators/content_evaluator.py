"""Content evaluation system for the SEO blog generator."""

import re
from typing import Dict, List, cast

from bs4 import BeautifulSoup, Tag
from textstat import textstat

from src.data.models import BlogArticle
from src.utils.logger import get_logger
from src.utils.text_utils import strip_html

logger = get_logger(__name__)


class ContentEvaluator:
    """Evaluator for blog content quality and SEO metrics."""

    def __init__(self):
        """Initialize the content evaluator."""
        self.metrics = {}
        self.thresholds = {
            "min_word_count": 1500,
            "max_word_count": 2500,
            "min_readability_score": 60,
            "max_readability_score": 70,
            "keyword_density_min": 0.01,  # 1%
            "keyword_density_max": 0.02,  # 2%
            "meta_description_min_length": 150,
            "meta_description_max_length": 160,
            "title_tag_min_length": 50,
            "title_tag_max_length": 60,
        }

    async def evaluate_article(self, article: BlogArticle) -> Dict[str, float]:
        """Evaluate a blog article across all metrics.

        Args:
            article: Blog article to evaluate

        Returns:
            Dictionary of evaluation scores
        """
        try:
            seo_metrics = await self.evaluate_seo(article)
            quality_metrics = await self.evaluate_quality(article)
            technical_metrics = await self.evaluate_technical(article)
            business_metrics = await self.evaluate_business_metrics(article)

            # Combine all metrics
            all_metrics = {
                **seo_metrics,
                **quality_metrics,
                **technical_metrics,
                **business_metrics,
            }

            # Calculate overall scores
            overall_scores = {
                "seo_score": self._calculate_category_score(seo_metrics),
                "quality_score": self._calculate_category_score(quality_metrics),
                "technical_score": self._calculate_category_score(technical_metrics),
                "business_score": self._calculate_category_score(business_metrics),
                "overall_score": self._calculate_overall_score(all_metrics),
            }

            return {**all_metrics, **overall_scores}

        except Exception as e:
            logger.error(f"Error evaluating article: {e}")
            raise

    async def evaluate_seo(self, article: BlogArticle) -> Dict[str, float]:
        """Evaluate SEO metrics for a blog article.

        Args:
            article: Blog article to evaluate

        Returns:
            Dictionary of SEO metrics
        """
        metrics = {}

        # Keyword density
        clean_content = strip_html(article.content)
        word_count = len(clean_content.split())

        # Calculate keyword density for primary keywords
        for keyword_data in article.cluster_keyword_data:
            keyword = keyword_data.keyword.lower()
            keyword_count = clean_content.lower().count(keyword)
            density = keyword_count / word_count if word_count > 0 else 0
            metrics[f"keyword_density_{keyword}"] = density

        # Meta description length
        meta_desc_length = len(article.meta_description)
        metrics["meta_description_length_score"] = self._score_range(
            meta_desc_length,
            self.thresholds["meta_description_min_length"],
            self.thresholds["meta_description_max_length"],
        )

        # Title tag length
        title_tag_length = len(article.title_tag)
        metrics["title_tag_length_score"] = self._score_range(
            title_tag_length,
            self.thresholds["title_tag_min_length"],
            self.thresholds["title_tag_max_length"],
        )

        # Heading structure
        metrics["heading_structure_score"] = self._evaluate_heading_structure(article.content)

        # Image optimization
        metrics["image_optimization_score"] = self._evaluate_images(article.image_details)

        return metrics

    async def evaluate_quality(self, article: BlogArticle) -> Dict[str, float]:
        """Evaluate content quality metrics.

        Args:
            article: Blog article to evaluate

        Returns:
            Dictionary of quality metrics
        """
        metrics = {}
        clean_content = strip_html(article.content)

        # Word count
        word_count = len(clean_content.split())
        metrics["word_count_score"] = self._score_range(
            word_count,
            self.thresholds["min_word_count"],
            self.thresholds["max_word_count"],
        )

        # Readability
        readability_score = textstat.flesch_reading_ease(clean_content)
        metrics["readability_score"] = self._score_range(
            readability_score,
            self.thresholds["min_readability_score"],
            self.thresholds["max_readability_score"],
        )

        return metrics

    async def evaluate_technical(self, article: BlogArticle) -> Dict[str, float]:
        """Evaluate technical metrics.

        Args:
            article: Blog article to evaluate

        Returns:
            Dictionary of technical metrics
        """
        metrics = {}

        # HTML structure validity
        metrics["html_validity_score"] = self._evaluate_html_structure(article.content)

        # Schema markup presence
        metrics["schema_markup_score"] = self._evaluate_schema_markup(article.content)

        return metrics

    async def evaluate_business_metrics(self, article: BlogArticle) -> Dict[str, float]:
        """Evaluate business-related metrics.

        Args:
            article: Blog article to evaluate

        Returns:
            Dictionary of business metrics
        """
        metrics = {}

        # Content uniqueness (placeholder)
        metrics["content_uniqueness_score"] = 1.0

        # Brand voice alignment (placeholder)
        metrics["brand_voice_score"] = 1.0

        return metrics

    def _score_range(self, value: float, min_value: float, max_value: float) -> float:
        """Score a value based on whether it falls within a desired range.

        Args:
            value: Value to score
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value

        Returns:
            Score between 0 and 1
        """
        if min_value <= value <= max_value:
            return 1.0
        elif value < min_value:
            return max(0, value / min_value)
        else:
            return max(0, max_value / value)

    def _evaluate_heading_structure(self, content: str) -> float:
        """Evaluate the heading structure of the content.

        Args:
            content: HTML content to evaluate

        Returns:
            Score between 0 and 1
        """
        soup = BeautifulSoup(content, "html.parser")

        # Check for presence of h1
        h1_tags = soup.find_all("h1")
        if not h1_tags or len(h1_tags) > 1:
            return 0.0

        # Check heading hierarchy
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not headings:
            return 0.0

        # Check if headings are in order
        current_level = 1
        for heading in headings:
            heading_tag = cast(Tag, heading)
            level = int(heading_tag.name[1])
            if level > current_level + 1:
                return 0.5  # Penalize skipped levels
            current_level = level

        return 1.0

    def _evaluate_images(self, image_details: List) -> float:
        """Evaluate image optimization.

        Args:
            image_details: List of image details

        Returns:
            Score between 0 and 1
        """
        if not image_details:
            return 0.0

        scores = []
        for image in image_details:
            # Check alt text
            has_alt = bool(image.alt_text and len(image.alt_text) > 10)
            # Check dimensions (if available)
            has_dimensions = bool(image.width and image.height)

            score = (has_alt + has_dimensions) / 2
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    def _evaluate_html_structure(self, content: str) -> float:
        """Evaluate HTML structure validity.

        Args:
            content: HTML content to evaluate

        Returns:
            Score between 0 and 1
        """
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Check for basic structure elements
            has_article = bool(soup.find("article"))
            has_sections = bool(soup.find_all("section"))
            has_paragraphs = bool(soup.find_all("p"))

            return (has_article + has_sections + has_paragraphs) / 3

        except Exception:
            return 0.0

    def _evaluate_schema_markup(self, content: str) -> float:
        """Evaluate schema.org markup presence.

        Args:
            content: HTML content to evaluate

        Returns:
            Score between 0 and 1
        """
        soup = BeautifulSoup(content, "html.parser")

        # Check for schema.org attributes
        schema_elements = soup.find_all(attrs={"itemtype": re.compile(r"schema.org")})
        if not schema_elements:
            return 0.0

        return 1.0

    def _calculate_category_score(self, metrics: Dict[str, float]) -> float:
        """Calculate the overall score for a category of metrics.

        Args:
            metrics: Dictionary of metrics and their scores

        Returns:
            Overall category score between 0 and 1
        """
        if not metrics:
            return 0.0
        return sum(metrics.values()) / len(metrics)

    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate the overall evaluation score.

        Args:
            metrics: Dictionary of all metrics

        Returns:
            Overall score between 0 and 1
        """
        return self._calculate_category_score(metrics)
