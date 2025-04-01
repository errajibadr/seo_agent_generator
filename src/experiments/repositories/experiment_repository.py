"""Repository for managing experiment results."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from src.agents.content_writer import BlogArticle
from src.experiments.experiment_config import ExperimentConfig, ModelConfig, PromptConfig
from src.experiments.experiment_runner import ExperimentResult
from src.utils.logger import get_logger
from src.utils.text_utils import sanitize_filename

logger = get_logger(__name__)


class ExperimentRepository:
    """Repository for managing experiment results.

    This class provides methods to save, load, and analyze experiment results
    from/to file storage, with a design that can be extended to use database storage.
    """

    def __init__(self, results_dir: Optional[Union[str, Path]] = None):
        """Initialize the experiment repository.

        Args:
            results_dir: Directory for storing results, defaults to src/experiments/results
        """
        if results_dir is None:
            # Default to project structure
            root_dir = Path(__file__).parent.parent.parent.parent
            results_dir = root_dir / "src" / "experiments" / "results"

        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True, parents=True)

    def save_result(self, result: ExperimentResult) -> None:
        """Save an experiment result to storage.

        Args:
            result: Experiment result to save
        """
        # Create directory for the experiment if it doesn't exist
        experiment_dir = self.results_dir / str(result.experiment_id)
        experiment_dir.mkdir(exist_ok=True)

        # Create a unique filename for the result (timestamp + model + prompt)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{sanitize_filename(result.model_config.name)}_{sanitize_filename(result.prompt_config.name)}.json"
        result_path = experiment_dir / filename

        # Convert result to a serializable dictionary
        result_dict = {
            "experiment_id": str(result.experiment_id),
            "timestamp": timestamp,
            "prompt_config": {
                "name": result.prompt_config.name,
                "description": result.prompt_config.description,
                # Don't store the full template to save space
                "template_length": len(result.prompt_config.template),
                "parameters": result.prompt_config.parameters,
            },
            "model_config": {k: v for k, v in result.model_config.__dict__.items()},
            "article": result.article.model_dump(),
            "evaluation_scores": result.evaluation_scores,
            "generation_time": result.generation_time,
            "token_usage": result.token_usage,
        }

        with open(result_path, "w") as f:
            json.dump(result_dict, f, indent=2)

        logger.info(f"Saved experiment result: {result_path}")

    def save_results(self, results: List[ExperimentResult]) -> None:
        """Save multiple experiment results to storage.

        Args:
            results: List of experiment results to save
        """
        for result in results:
            self.save_result(result)

    def get_experiment_results(self, experiment_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """Get all results for an experiment.

        Args:
            experiment_id: ID of the experiment

        Returns:
            List of experiment results
        """
        # Convert UUID to string if needed
        experiment_id_str = str(experiment_id)
        experiment_dir = self.results_dir / experiment_id_str

        if not experiment_dir.exists():
            logger.warning(f"No results found for experiment: {experiment_id_str}")
            return []

        results = []
        for result_file in experiment_dir.glob("*.json"):
            try:
                with open(result_file, "r") as f:
                    result_dict = json.load(f)
                results.append(result_dict)
            except Exception as e:
                logger.error(f"Error loading result file {result_file}: {e}")

        # Sort by timestamp
        results.sort(key=lambda x: x.get("timestamp", ""))
        return results

    def list_experiments(self) -> List[str]:
        """List all experiments with stored results.

        Returns:
            List of experiment IDs
        """
        return [d.name for d in self.results_dir.iterdir() if d.is_dir()]

    def get_experiment_summary(self, experiment_id: Union[str, UUID]) -> Dict[str, Any]:
        """Get a summary of experiment results.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Dictionary with experiment summary
        """
        results = self.get_experiment_results(experiment_id)

        if not results:
            return {
                "experiment_id": str(experiment_id),
                "num_results": 0,
                "metrics": {},
                "models": [],
                "prompts": [],
            }

        # Extract metrics across all results
        all_scores = {}
        models = set()
        prompts = set()
        total_generation_time = 0
        total_tokens = 0

        for result in results:
            # Collect unique models and prompts
            models.add(result["model_config"]["name"])
            prompts.add(result["prompt_config"]["name"])

            # Sum up generation time
            total_generation_time += result["generation_time"]

            # Sum up token usage if available
            if result.get("token_usage"):
                if "total" in result["token_usage"]:
                    total_tokens += result["token_usage"]["total"]
                elif "completion" in result["token_usage"]:
                    total_tokens += result["token_usage"]["completion"]

            # Collect all evaluation scores
            for metric, score in result["evaluation_scores"].items():
                if metric not in all_scores:
                    all_scores[metric] = []
                all_scores[metric].append(score)

        # Calculate averages for metrics
        avg_metrics = {}
        for metric, scores in all_scores.items():
            avg_metrics[metric] = sum(scores) / len(scores)

        return {
            "experiment_id": str(experiment_id),
            "num_results": len(results),
            "metrics": avg_metrics,
            "models": list(models),
            "prompts": list(prompts),
            "avg_generation_time": total_generation_time / len(results),
            "total_tokens": total_tokens,
        }

    def compare_experiments(self, experiment_ids: List[Union[str, UUID]]) -> Dict[str, Any]:
        """Compare multiple experiments.

        Args:
            experiment_ids: List of experiment IDs to compare

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "experiments": {},
            "metrics": {},
        }

        all_metrics = set()

        # Get summaries for all experiments
        for exp_id in experiment_ids:
            summary = self.get_experiment_summary(exp_id)
            comparison["experiments"][str(exp_id)] = summary

            # Collect all metrics
            for metric in summary["metrics"]:
                all_metrics.add(metric)

        # Compare metrics across experiments
        for metric in all_metrics:
            comparison["metrics"][metric] = {
                str(exp_id): comparison["experiments"][str(exp_id)]["metrics"].get(metric)
                for exp_id in experiment_ids
            }

        return comparison
