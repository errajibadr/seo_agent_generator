"""Example script for running content generation experiments."""

import asyncio
import os
from pathlib import Path

from src.experiments import ExperimentManager, ModelConfig, PromptConfig
from src.prompts.blog_post_prompt import blog_post_prompt
from src.utils.logger import get_logger

# Setup logging
logger = get_logger(__name__)


def ensure_directories():
    """Ensure all required directories exist."""
    # Create base directories
    base_dirs = [
        "src/experiments/config/model_configs",
        "src/experiments/config/prompt_configs",
        "src/experiments/config/experiment_configs",
        "src/experiments/data/keyword_clusters",
        "src/experiments/results",
    ]

    for dir_path in base_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")


async def main():
    """Run experiments for content generation."""
    # Ensure all directories exist
    ensure_directories()

    # Initialize experiment manager
    experiment_manager = ExperimentManager()

    # Create model configurations
    model_configs = [
        ModelConfig(
            name="deepseek/deepseek-chat-v3-0324",
            temperature=0.7,
            max_tokens=3000,
        ),
        # ModelConfig(
        #     name="anthropic/claude-3.7-sonnet",
        #     temperature=0.7,
        #     max_tokens=3000,
        # ),
        ModelConfig(
            name="google/gemini-2.0-flash-001",
            temperature=0.7,
            max_tokens=3000,
        ),
    ]

    # Create prompt configurations
    default_prompt = PromptConfig(
        name="default_blog_source",
        template=blog_post_prompt,
        description="Default blog post prompt",
    )

    creative_prompt = PromptConfig(
        name="creative_blog_v0.0.1_20250331",
        template=blog_post_prompt.replace(
            "You are a professional SEO content writer",
            "You are a creative and engaging SEO content writer with a unique voice",
        ),
        description="More creative blog post prompt",
    )

    logger.info("Saving model and prompt configurations...")

    # Save configurations
    try:
        for model in model_configs:
            experiment_manager.config_repo.save_model_config(model)
            logger.info(f"Saved model config: {model.name}")

        experiment_manager.config_repo.save_prompt_config(default_prompt)
        experiment_manager.config_repo.save_prompt_config(creative_prompt)
    except Exception as e:
        logger.error(f"Error saving configurations: {e}")
        raise

    # Import keyword data from CSV
    # Look in multiple locations for the CSV file
    potential_csv_paths = [
        os.path.join(os.path.dirname(__file__), "data", "éducateur-canin_clusters_2025-03-28.csv"),
        os.path.join(os.path.dirname(__file__), "data", "keywords.csv"),
        # Add more potential paths as needed
    ]

    csv_found = False
    for csv_path in potential_csv_paths:
        if os.path.exists(csv_path):
            csv_found = True
            try:
                logger.info(f"Attempting to import keyword data from {csv_path}")
                experiment_manager.keyword_repo.import_from_csv(
                    csv_path=csv_path,
                    cluster_name="first_cluster_test",
                    tags=["test", "seo"],
                )
                logger.info(f"Successfully imported keyword data from {csv_path}")
                break
            except Exception as e:
                logger.error(f"Error importing keyword data from {csv_path}: {e}")

    if not csv_found:
        logger.warning("No CSV files found. Creating dummy keyword data.")
        # Create a dummy keyword cluster for testing
        from src.data.models import KeywordData

        dummy_keywords = [
            KeywordData(
                keyword="best seo practices",
                topic="SEO",
                page_type="blog",
                intent="informational",
                volume=1000,
                keyword_difficulty=45.5,
            ),
            KeywordData(
                keyword="seo for beginners",
                topic="SEO",
                page_type="blog",
                intent="informational",
                volume=2000,
                keyword_difficulty=35.5,
            ),
        ]

        experiment_manager.keyword_repo.save_cluster(
            name="test_keywords",
            keywords=dummy_keywords,
            tags=["test", "seo"],
        )
        logger.info("Created dummy keyword cluster: test_keywords")

    # Create experiment
    try:
        experiment = experiment_manager.create_experiment(
            name="seo_blog_comparison",
            description="Comparing different models and prompts for SEO blog generation",
            model_config_names=[model.name for model in model_configs],
            prompt_config_names=[default_prompt.name, creative_prompt.name],
            num_samples=1,  # Number of articles to generate per config
        )

        logger.info(f"Created experiment: {experiment.name} ({experiment.id})")
    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        raise

    # List available resources
    resources = experiment_manager.list_available_resources()
    logger.info(f"Available resources: {resources}")

    # Run experiment
    should_run = input("Run the experiment? (y/n): ").lower().strip() == "y"

    if should_run:
        try:
            results = await experiment_manager.run_experiment(
                experiment_name="seo_blog_comparison",
                cluster_names=["test_keywords"] if not csv_found else ["first_cluster_test"],
            )

            logger.info(
                f"Experiment completed with {sum(len(r) for r in results.values())} results"
            )

            # Get experiment summary
            summary = experiment_manager.get_experiment_summary("seo_blog_comparison")
            logger.info(f"Experiment summary: {summary}")
        except Exception as e:
            logger.error(f"Error running experiment: {e}")
    else:
        logger.info("Experiment setup complete. Run manually when ready.")


if __name__ == "__main__":
    asyncio.run(main())
