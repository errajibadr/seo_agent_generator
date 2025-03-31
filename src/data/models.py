"""Data models for the SEO blog generator."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class KeywordData(BaseModel):
    """Model for keyword data from CSV input."""

    database: str = Field(default="fr")
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
    content_references: Optional[dict[str, str]] = None
    competitors: Optional[dict[str, str]] = None

    def to_prompt_context(self) -> dict:
        """Convert keyword data to a format suitable for prompt context.

        Returns:
            dict: Keyword data formatted for prompt context
        """
        return {
            "primary_keyword": self.keyword,
            "importance_in_cluster": self.importance_in_cluster,
            "intent": self.intent or "informational",
            "volume": self.volume or 0,
            "competition": self.competitive_density or 0.0,
            "content_references": list(self.content_references.values())[:2]
            if self.content_references
            else [],
        }


class ImageDetail(BaseModel):
    """Model for image details."""

    placeholder: Optional[str] = None
    alt_text: str
    description: str
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    generated: bool = False


class BlogArticle(BaseModel):
    """Model for a blog article."""

    title: str
    slug: str
    publication_date: str = Field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))
    reading_time: str
    table_of_contents: Optional[str] = None
    content: str
    article_type: str
    article_types_secondary: List[str]
    article_summary: str
    title_tag: str
    meta_description: str
    cluster_keyword_data: List[KeywordData]
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
            "Contenu article": self.content,
            "Type d'article": self.article_type,
            "Type d'article 2-8": ", ".join(self.article_types_secondary),
            "Résumé de l'article": self.article_summary,
            "Balise title": self.title_tag,
            "META DESCRIPTION": self.meta_description,
        }
