"""Manager for experiment orchestration and execution."""

from typing import Any, Dict, List, Optional

from src.experiments.experiment_config import ExperimentConfig, ModelConfig, PromptConfig
from src.experiments.experiment_runner import ExperimentResult, ExperimentRunner
from src.experiments.repositories.config_repository import ConfigRepository
from src.experiments.repositories.experiment_repository import ExperimentRepository
from src.experiments.repositories.keyword_repository import KeywordRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExperimentManager:
    """Manager for orchestrating experiment execution and analysis.

    This class provides high-level methods to create, run, and analyze
    experiments using the repositories for configuration, keywords, and results.
    """

    def __init__(
        self,
        config_repo: Optional[ConfigRepository] = None,
        keyword_repo: Optional[KeywordRepository] = None,
        experiment_repo: Optional[ExperimentRepository] = None,
    ):
        """Initialize the experiment manager.

        Args:
            config_repo: Repository for configurations
            keyword_repo: Repository for keyword data
            experiment_repo: Repository for experiment results
        """
        self.config_repo = config_repo or ConfigRepository()
        self.keyword_repo = keyword_repo or KeywordRepository()
        self.experiment_repo = experiment_repo or ExperimentRepository()

    def create_experiment(
        self,
        name: str,
        description: Optional[str] = None,
        model_config_names: Optional[List[str]] = None,
        prompt_config_names: Optional[List[str]] = None,
        model_configs: Optional[List[ModelConfig]] = None,
        prompt_configs: Optional[List[PromptConfig]] = None,
        num_samples: int = 1,
    ) -> ExperimentConfig:
        """Create a new experiment configuration.

        Args:
            name: Name of the experiment
            description: Optional description
            model_config_names: Names of existing model configs to include
            prompt_config_names: Names of existing prompt configs to include
            model_configs: New model configurations to include
            prompt_configs: New prompt configurations to include
            num_samples: Number of samples to generate per config combination

        Returns:
            Created experiment configuration
        """
        # Load existing configs if names are provided
        all_model_configs = []
        all_prompt_configs = []

        if model_config_names:
            for model_name in model_config_names:
                try:
                    config = self.config_repo.load_model_config(model_name)
                    all_model_configs.append(config)
                except FileNotFoundError:
                    logger.warning(f"Model config not found: {model_name}")

        if prompt_config_names:
            for prompt_name in prompt_config_names:
                try:
                    config = self.config_repo.load_prompt_config(prompt_name)
                    all_prompt_configs.append(config)
                except FileNotFoundError:
                    logger.warning(f"Prompt config not found: {prompt_name}")

        # Add new configs
        if model_configs:
            all_model_configs.extend(model_configs)

            # Save new model configs for future use
            for config in model_configs:
                self.config_repo.save_model_config(config)

        if prompt_configs:
            all_prompt_configs.extend(prompt_configs)

            # Save new prompt configs for future use
            for config in prompt_configs:
                self.config_repo.save_prompt_config(config)

        # Create experiment config
        experiment_config = ExperimentConfig(
            name=name,
            description=description,
            prompt_configs=all_prompt_configs,
            model_configs=all_model_configs,
            num_samples=num_samples,
        )

        # Save experiment config
        self.config_repo.save_experiment_config(experiment_config)

        logger.info(
            f"Created experiment: {name} with {len(all_model_configs)} models and {len(all_prompt_configs)} prompts"
        )
        return experiment_config

    async def run_experiment(
        self,
        experiment_name: str,
        cluster_names: List[str],
    ) -> Dict[str, List[ExperimentResult]]:
        """Run an experiment with the given keyword clusters.

        Args:
            experiment_name: Name of the experiment to run
            cluster_names: Names of keyword clusters to use

        Returns:
            Dictionary mapping cluster names to lists of experiment results
        """
        # Load experiment config
        try:
            experiment_config = self.config_repo.load_experiment_config(experiment_name)
        except FileNotFoundError:
            raise ValueError(f"Experiment not found: {experiment_name}")

        runner = ExperimentRunner(experiment_config)

        results_by_cluster = {}

        for cluster_name in cluster_names:
            try:
                cluster_data = self.keyword_repo.get_cluster(cluster_name)

                logger.info(f"Running experiment {experiment_name} with cluster {cluster_name}")
                results = await runner.run_all_experiments(cluster_data)

                self.experiment_repo.save_results(results)

                results_by_cluster[cluster_name] = results

            except FileNotFoundError:
                logger.error(f"Keyword cluster not found: {cluster_name}")
            except Exception as e:
                logger.error(f"Error running experiment with cluster {cluster_name}: {e}")

        return results_by_cluster

    def get_experiment_summary(self, experiment_name: str) -> Dict[str, Any]:
        """Get a summary of experiment results.

        Args:
            experiment_name: Name of the experiment

        Returns:
            Dictionary with experiment summary
        """
        try:
            # Load experiment config
            experiment_config = self.config_repo.load_experiment_config(experiment_name)

            # Get experiment summary
            summary = self.experiment_repo.get_experiment_summary(experiment_config.id)

            # Add experiment metadata
            summary["name"] = experiment_config.name
            summary["description"] = experiment_config.description
            summary["created_at"] = experiment_config.created_at.isoformat()

            return summary

        except FileNotFoundError:
            logger.warning(f"Experiment not found: {experiment_name}")
            return {
                "name": experiment_name,
                "error": "Experiment not found",
            }

    def compare_experiments(self, experiment_names: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments.

        Args:
            experiment_names: List of experiment names to compare

        Returns:
            Dictionary with comparison results
        """
        # Load experiment configs and IDs
        experiment_ids = []
        experiment_data = {}

        for name in experiment_names:
            try:
                config = self.config_repo.load_experiment_config(name)
                experiment_ids.append(config.id)
                experiment_data[str(config.id)] = {
                    "name": name,
                    "description": config.description,
                    "created_at": config.created_at.isoformat(),
                }
            except FileNotFoundError:
                logger.warning(f"Experiment not found: {name}")

        # Get comparison from repository
        comparison = self.experiment_repo.compare_experiments(experiment_ids)

        # Add experiment metadata
        for exp_id, exp_info in experiment_data.items():
            if exp_id in comparison["experiments"]:
                comparison["experiments"][exp_id].update(exp_info)

        return comparison

    def list_available_resources(self) -> Dict[str, Any]:
        """List all available resources for experiments.

        Returns:
            Dictionary with available model configs, prompt configs,
            experiments, and keyword clusters
        """
        return {
            "model_configs": self.config_repo.list_model_configs(),
            "prompt_configs": self.config_repo.list_prompt_configs(),
            "experiments": self.config_repo.list_experiment_configs(),
            "keyword_clusters": self.keyword_repo.list_clusters(),
        }
