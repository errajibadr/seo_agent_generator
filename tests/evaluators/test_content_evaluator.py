"""Unit tests for the ContentEvaluator class."""

from datetime import datetime

import pytest

from src.data.models import BlogArticle, ImageDetail, KeywordData
from src.evaluators.content_evaluator import ContentEvaluator


@pytest.fixture
def evaluator() -> ContentEvaluator:
    """Create a ContentEvaluator instance for testing."""
    return ContentEvaluator()


@pytest.fixture
def sample_keyword_data() -> list[KeywordData]:
    """Create sample keyword data for testing."""
    return [
        KeywordData(
            database="test",
            keyword="test keyword",
            topic="test topic",
            page_type="article",
            importance_in_cluster=0.5,
            volume=100,
            intent="informational",
        )
    ]


@pytest.fixture
def sample_article(sample_keyword_data: list[KeywordData]) -> BlogArticle:
    """Create a sample blog article for testing."""
    return BlogArticle(
        title="Test Article",
        slug="test-article",
        publication_date=datetime.now().strftime("%d/%m/%Y"),
        reading_time="5 minutes",
        content="""
        <article>
            <h1>Test Article Title</h1>
            <section>
                <h2>First Section</h2>
                <p>This is a test paragraph containing the test keyword.</p>
                <h3>Subsection</h3>
                <p>Another paragraph with content.</p>
            </section>
            <section>
                <h2>Second Section</h2>
                <p>More test content here.</p>
                <img src="test.jpg" alt="A detailed test image" width="800" height="600">
            </section>
            <div itemscope itemtype="http://schema.org/Article">
                <meta itemprop="name" content="Test Article">
            </div>
        </article>
        """,
        article_type="guide",
        article_types_secondary=["tutorial", "how-to"],
        article_summary="A test article for unit testing",
        title_tag="Test Article - Perfect Length Title Tag for SEO Testing",
        meta_description="This is a meta description that has the perfect length for SEO purposes and includes relevant keywords for better search engine optimization 12345678.",
        cluster_keyword_data=sample_keyword_data,
        image_details=[
            ImageDetail(
                alt_text="A detailed test image",
                description="Test image description",
                url="test.jpg",
                width=800,
                height=600,
            )
        ],
    )


@pytest.mark.asyncio
async def test_evaluate_article_overall(evaluator: ContentEvaluator, sample_article: BlogArticle):
    """Test that article evaluation returns all expected score categories."""
    scores = await evaluator.evaluate_article(sample_article)

    assert "seo_score" in scores
    assert "quality_score" in scores
    assert "technical_score" in scores
    assert "business_score" in scores
    assert "overall_score" in scores

    assert all(0 <= score <= 1 for score in scores.values())


@pytest.mark.asyncio
async def test_evaluate_seo_metrics(evaluator: ContentEvaluator, sample_article: BlogArticle):
    """Test SEO metrics evaluation."""
    seo_metrics = await evaluator.evaluate_seo(sample_article)

    # Check keyword density
    assert "keyword_density_test keyword" in seo_metrics
    assert 0 <= seo_metrics["keyword_density_test keyword"] <= 1

    # Check meta description length
    assert "meta_description_length_score" in seo_metrics
    assert seo_metrics["meta_description_length_score"] == 1.0  # Should be perfect length

    # Check title tag length
    assert "title_tag_length_score" in seo_metrics
    assert seo_metrics["title_tag_length_score"] == 1.0  # Should be perfect length

    # Check heading structure
    assert "heading_structure_score" in seo_metrics
    assert seo_metrics["heading_structure_score"] == 1.0  # Should be perfect structure

    # Check image optimization
    assert "image_optimization_score" in seo_metrics
    assert (
        seo_metrics["image_optimization_score"] == 1.0
    )  # Should have proper alt text and dimensions


@pytest.mark.asyncio
async def test_evaluate_quality_metrics(evaluator: ContentEvaluator, sample_article: BlogArticle):
    """Test content quality metrics evaluation."""
    quality_metrics = await evaluator.evaluate_quality(sample_article)

    assert "word_count_score" in quality_metrics
    assert "readability_score" in quality_metrics
    assert all(0 <= score <= 1 for score in quality_metrics.values())


@pytest.mark.asyncio
async def test_evaluate_technical_metrics(evaluator: ContentEvaluator, sample_article: BlogArticle):
    """Test technical metrics evaluation."""
    technical_metrics = await evaluator.evaluate_technical(sample_article)

    assert "html_validity_score" in technical_metrics
    assert technical_metrics["html_validity_score"] == 1.0  # Should have valid HTML structure

    assert "schema_markup_score" in technical_metrics
    assert technical_metrics["schema_markup_score"] == 1.0  # Should have schema.org markup


@pytest.mark.asyncio
async def test_evaluate_business_metrics(evaluator: ContentEvaluator, sample_article: BlogArticle):
    """Test business metrics evaluation."""
    business_metrics = await evaluator.evaluate_business_metrics(sample_article)

    assert "content_uniqueness_score" in business_metrics
    assert "brand_voice_score" in business_metrics
    assert all(0 <= score <= 1 for score in business_metrics.values())


def test_score_range(evaluator: ContentEvaluator):
    """Test the _score_range helper method."""
    # Test perfect score
    assert evaluator._score_range(5, 1, 10) == 1.0

    # Test below minimum
    assert evaluator._score_range(0.5, 1, 10) == 0.5

    # Test above maximum
    assert evaluator._score_range(20, 1, 10) == 0.5


@pytest.mark.asyncio
async def test_evaluate_article_with_issues(
    evaluator: ContentEvaluator, sample_article: BlogArticle
):
    """Test article evaluation with common issues."""
    # Create an article with various issues
    bad_article = sample_article.model_copy()
    bad_article.content = """
    <div>
        <h2>Missing H1</h2>
        <p>Content without proper structure.</p>
        <img src="test.jpg">
    </div>
    """
    bad_article.meta_description = "Too short"
    bad_article.title_tag = "Short"

    scores = await evaluator.evaluate_article(bad_article)

    # SEO scores should be lower
    assert scores["seo_score"] < 1.0
    assert scores["technical_score"] < 1.0
    assert scores["meta_description_length_score"] < 1.0
    assert scores["title_tag_length_score"] < 1.0


def test_evaluate_heading_structure(evaluator: ContentEvaluator):
    """Test heading structure evaluation with different scenarios."""
    # Perfect structure
    good_html = """
    <article>
        <h1>Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
    </article>
    """
    assert evaluator._evaluate_heading_structure(good_html) == 1.0

    # Missing H1
    bad_html = """
    <article>
        <h2>Section</h2>
        <h3>Subsection</h3>
    </article>
    """
    assert evaluator._evaluate_heading_structure(bad_html) == 0.0

    # Skipped level
    skip_html = """
    <article>
        <h1>Title</h1>
        <h3>Subsection</h3>
    </article>
    """
    assert evaluator._evaluate_heading_structure(skip_html) == 0.5
