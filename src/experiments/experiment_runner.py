from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from src.agents.content_writer import BlogArticle, ContentWriter
from src.config import Config
from src.data.models import KeywordData
from src.evaluators.content_evaluator import ContentEvaluator
from src.experiments.experiment_config import ExperimentConfig, ModelConfig, PromptConfig
from src.services.openrouter_service import OpenRouterService
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExperimentResult:
    """Results from a single experiment run"""

    experiment_id: UUID
    prompt_config: PromptConfig
    model_config: ModelConfig
    article: BlogArticle
    evaluation_scores: Dict[str, float]
    generation_time: float
    token_usage: Optional[Dict[str, int]] = None


class ExperimentRunner:
    """Runner for content generation experiments"""

    def __init__(self, config: ExperimentConfig):
        """Initialize the experiment runner.

        Args:
            config: Experiment configuration
        """
        self.config = config
        self.evaluator = ContentEvaluator()

    async def run_experiment(
        self,
        prompt_config: PromptConfig,
        model_config: ModelConfig,
        cluster_data: List[KeywordData],
    ) -> ExperimentResult:
        """Run a single experiment with given prompt and model configs.

        Args:
            prompt_config: Prompt configuration
            model_config: Model configuration
            cluster_data: Keyword data for content generation

        Returns:
            Experiment result
        """
        start_time = datetime.utcnow()

        # Create OpenRouter service with model config
        config = Config(
            default_model=model_config.name,
            default_model_params={k: v for k, v in model_config.__dict__.items() if k != "name"},
        )
        openrouter_service = OpenRouterService(config=config)

        # Create content writer with configured service and prompt
        content_writer = ContentWriter(
            openrouter_service=openrouter_service, prompt_template=prompt_config.template
        )

        # Generate blog article
        cluster_name = cluster_data[0].topic if cluster_data else "Untitled"
        article = await content_writer.generate_blog(cluster_name, cluster_data)

        scores = await self.evaluator.evaluate_article(article)

        # Calculate generation time
        generation_time = (datetime.utcnow() - start_time).total_seconds()

        # Get token usage if tracking is enabled
        token_usage = None
        if self.config.track_token_usage and hasattr(openrouter_service, "last_token_usage"):
            token_usage = getattr(openrouter_service, "last_token_usage", None)

        return ExperimentResult(
            experiment_id=self.config.id,
            prompt_config=prompt_config,
            model_config=model_config,
            article=article,
            evaluation_scores=scores,
            generation_time=generation_time,
            token_usage=token_usage,
        )

    async def run_all_experiments(self, cluster_data: List[KeywordData]) -> List[ExperimentResult]:
        """Run experiments for all prompt and model configurations.

        Args:
            cluster_data: Keyword data for content generation

        Returns:
            List of experiment results
        """
        results = []
        for prompt_config in self.config.prompt_configs:
            for model_config in self.config.model_configs:
                for _ in range(self.config.num_samples):
                    try:
                        result = await self.run_experiment(
                            prompt_config, model_config, cluster_data
                        )
                        results.append(result)
                    except Exception as e:
                        logger.error(
                            f"Error running experiment with prompt {prompt_config.name} "
                            f"and model {model_config.name}: {e}"
                        )
        return results
