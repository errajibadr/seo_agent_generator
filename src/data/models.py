"""Data models for the SEO blog generator."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class KeywordData(BaseModel):
    """Model for keyword data from CSV input."""

    database: str
    keyword: str
    seed_keyword: Optional[str] = None
    page: Optional[str] = None
    topic: str
    page_type: str
    importance_in_cluster: Optional[float] = None
    tags: Optional[List[str]] = None
    volume: Optional[int] = None
    keyword_difficulty: Optional[float] = None
    cpc_usd: Optional[float] = None
    competitive_density: Optional[float] = None
    number_of_results: Optional[int] = None
    intent: Optional[str] = None
    serp_features: Optional[List[str]] = None
    trend: Optional[str] = None
    click_potential: Optional[str] = None
    content_references: Optional[str] = None
    competitors: Optional[List[str]] = None

    def to_prompt_context(self) -> dict:
        """Convert keyword data to a format suitable for prompt context.

        Returns:
            dict: Keyword data formatted for prompt context
        """
        return {
            "primary_keyword": self.keyword,
            "secondary_keywords": [self.seed_keyword] if self.seed_keyword else [],
            "related_keywords": self.tags or [],
            "topic": self.topic,
            "intent": self.intent or "informational",
            "volume": self.volume or 0,
            "competition": self.competitive_density or 0.0,
        }


class ImageDetail(BaseModel):
    """Model for image details."""

    alt_text: str
    description: str
    url: Optional[HttpUrl] = None
    width: Optional[int] = None
    height: Optional[int] = None
    generated: bool = False


class BlogArticle(BaseModel):
    """Model for a blog article."""

    title: str
    slug: str
    publication_date: str = Field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))
    reading_time: str
    table_of_contents: str
    content: str
    article_type: str
    article_types_secondary: List[str]
    article_summary: str
    title_tag: str
    meta_description: str
    keyword_data: KeywordData
    image_details: List[ImageDetail] = []

    def to_json_dict(self) -> dict:
        """Convert the article to a JSON-serializable dictionary.

        Returns:
            dict: JSON-serializable dictionary
        """
        return {
            "Titre": self.title,
            "Slug": self.slug,
            "Date de publication": self.publication_date,
            "Durée de lecture": self.reading_time,
            "Table des matières": self.table_of_contents,
            "Contenu article": self.content,
            "Type d'article": self.article_type,
            "Type d'article 2-8": ", ".join(self.article_types_secondary),
            "Résumé de l'article": self.article_summary,
            "Balise title": self.title_tag,
            "META DESCRIPTION": self.meta_description,
        }
