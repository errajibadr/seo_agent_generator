from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class PromptConfig:
    name: str
    template: str
    description: Optional[str] = None
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class ModelConfig:
    name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)


@dataclass
class ExperimentConfig:
    """Configuration for content generation experiments"""

    # Required fields
    name: str
    prompt_configs: List[PromptConfig]
    model_configs: List[ModelConfig]

    # Optional fields with defaults
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    num_samples: int = 5  # Number of articles to generate per config

    # Evaluation settings
    min_words: int = 800
    max_words: int = 2000
    target_readability_score: float = 60.0  # Flesch reading ease
    min_keyword_density: float = 0.01
    max_keyword_density: float = 0.03

    # Cost tracking
    track_token_usage: bool = True
    max_cost_per_article: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert config to dictionary for storage"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "prompt_configs": [
                {
                    "name": p.name,
                    "template": p.template,
                    "parameters": p.parameters,
                    "description": p.description,
                }
                for p in self.prompt_configs
            ],
            "model_configs": [
                {
                    "name": m.name,
                    "temperature": m.temperature,
                    "max_tokens": m.max_tokens,
                    "top_p": m.top_p,
                    "frequency_penalty": m.frequency_penalty,
                    "presence_penalty": m.presence_penalty,
                    "stop_sequences": m.stop_sequences,
                }
                for m in self.model_configs
            ],
            "num_samples": self.num_samples,
            "evaluation_settings": {
                "min_words": self.min_words,
                "max_words": self.max_words,
                "target_readability_score": self.target_readability_score,
                "min_keyword_density": self.min_keyword_density,
                "max_keyword_density": self.max_keyword_density,
            },
            "cost_tracking": {
                "track_token_usage": self.track_token_usage,
                "max_cost_per_article": self.max_cost_per_article,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExperimentConfig":
        """Create config from dictionary"""
        prompt_configs = [PromptConfig(**p) for p in data["prompt_configs"]]
        model_configs = [ModelConfig(**m) for m in data["model_configs"]]

        return cls(
            name=data["name"],
            prompt_configs=prompt_configs,
            model_configs=model_configs,
            id=UUID(data["id"]),
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"]),
            num_samples=data["num_samples"],
            min_words=data["evaluation_settings"]["min_words"],
            max_words=data["evaluation_settings"]["max_words"],
            target_readability_score=data["evaluation_settings"]["target_readability_score"],
            min_keyword_density=data["evaluation_settings"]["min_keyword_density"],
            max_keyword_density=data["evaluation_settings"]["max_keyword_density"],
            track_token_usage=data["cost_tracking"]["track_token_usage"],
            max_cost_per_article=data["cost_tracking"]["max_cost_per_article"],
        )
