"""Repository for managing experiment configurations."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.experiments.experiment_config import ExperimentConfig, ModelConfig, PromptConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigRepository:
    """Repository for managing experiment configurations.

    This class provides methods to load and save experiment configurations
    from/to file storage, with a design that can be extended to use database storage.
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """Initialize the configuration repository.

        Args:
            config_dir: Directory for storing configurations, defaults to src/experiments/config
        """
        if config_dir is None:
            # Default to project structure
            # should be in root_repo/src/experiments/config
            root_dir = Path(__file__).parent.parent.parent.parent
            config_dir = root_dir / "src" / "experiments" / "config"

        self.config_dir = Path(config_dir)
        self.model_config_dir = self.config_dir / "model_configs"
        self.prompt_config_dir = self.config_dir / "prompt_configs"
        self.experiment_config_dir = self.config_dir / "experiment_configs"

        # Create directories if they don't exist
        self.model_config_dir.mkdir(exist_ok=True, parents=True)
        self.prompt_config_dir.mkdir(exist_ok=True, parents=True)
        self.experiment_config_dir.mkdir(exist_ok=True, parents=True)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a name to be used as a filename.

        Args:
            name: Name to sanitize

        Returns:
            Sanitized name safe for use as a filename
        """
        # Replace characters that are invalid in filenames
        # Replace : / \ * ? " < > | with _
        sanitized = re.sub(r'[:\\/*?"<>|]', "_", name)

        # Also replace spaces with underscores for better compatibility
        sanitized = sanitized.replace(" ", "_")

        return sanitized

    # Model config methods
    def save_model_config(self, config: ModelConfig) -> None:
        """Save a model configuration to storage.

        Args:
            config: Model configuration to save
        """
        # Sanitize the model name for filename
        safe_name = self._sanitize_filename(config.name)
        file_path = self.model_config_dir / f"{safe_name}.json"

        with open(file_path, "w") as f:
            # Convert dataclass to dict and save as JSON
            config_dict = {k: v for k, v in config.__dict__.items()}
            json.dump(config_dict, f, indent=2)

        logger.info(f"Saved model config: {config.name}")

    def load_model_config(self, name: str) -> ModelConfig:
        """Load a model configuration from storage.

        Args:
            name: Name of the model configuration

        Returns:
            Loaded model configuration

        Raises:
            FileNotFoundError: If configuration does not exist
        """
        # Sanitize the model name for filename
        safe_name = self._sanitize_filename(name)
        file_path = self.model_config_dir / f"{safe_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Model config not found: {name}")

        with open(file_path, "r") as f:
            config_dict = json.load(f)

        return ModelConfig(**config_dict)

    def list_model_configs(self) -> List[str]:
        """List all available model configurations.

        Returns:
            List of model configuration names
        """
        config_files = self.model_config_dir.glob("*.json")
        # Note: we return the original names which may be sanitized in the files
        # We'd need to store a mapping if we want to recover original names
        return [file.stem for file in config_files]

    # Prompt config methods
    def save_prompt_config(self, config: PromptConfig) -> None:
        """Save a prompt configuration to storage.

        Args:
            config: Prompt configuration to save
        """
        # Sanitize the prompt name for filename
        safe_name = self._sanitize_filename(config.name)
        file_path = self.prompt_config_dir / f"{safe_name}.json"

        with open(file_path, "w") as f:
            # Convert dataclass to dict and save as JSON
            config_dict = {k: v for k, v in config.__dict__.items()}
            json.dump(config_dict, f, indent=2)

        logger.info(f"Saved prompt config: {config.name}")

    def load_prompt_config(self, name: str) -> PromptConfig:
        """Load a prompt configuration from storage.

        Args:
            name: Name of the prompt configuration

        Returns:
            Loaded prompt configuration

        Raises:
            FileNotFoundError: If configuration does not exist
        """
        # Sanitize the prompt name for filename
        safe_name = self._sanitize_filename(name)
        file_path = self.prompt_config_dir / f"{safe_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt config not found: {name}")

        with open(file_path, "r") as f:
            config_dict = json.load(f)

        return PromptConfig(**config_dict)

    def list_prompt_configs(self) -> List[str]:
        """List all available prompt configurations.

        Returns:
            List of prompt configuration names
        """
        config_files = self.prompt_config_dir.glob("*.json")
        return [file.stem for file in config_files]

    # Experiment config methods
    def save_experiment_config(self, config: ExperimentConfig) -> None:
        """Save an experiment configuration to storage.

        Args:
            config: Experiment configuration to save
        """
        # Sanitize the experiment name for filename
        safe_name = self._sanitize_filename(config.name)
        file_path = self.experiment_config_dir / f"{safe_name}.json"

        with open(file_path, "w") as f:
            json.dump(config.to_dict(), f, indent=2)

        logger.info(f"Saved experiment config: {config.name}")

    def load_experiment_config(self, name: str) -> ExperimentConfig:
        """Load an experiment configuration from storage.

        Args:
            name: Name of the experiment configuration

        Returns:
            Loaded experiment configuration

        Raises:
            FileNotFoundError: If configuration does not exist
        """
        # Sanitize the experiment name for filename
        safe_name = self._sanitize_filename(name)
        file_path = self.experiment_config_dir / f"{safe_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Experiment config not found: {name}")

        with open(file_path, "r") as f:
            config_dict = json.load(f)

        return ExperimentConfig.from_dict(config_dict)

    def list_experiment_configs(self) -> List[str]:
        """List all available experiment configurations.

        Returns:
            List of experiment configuration names
        """
        config_files = self.experiment_config_dir.glob("*.json")
        return [file.stem for file in config_files]
