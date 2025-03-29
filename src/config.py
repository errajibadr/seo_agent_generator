"""Configuration for the SEO blog generator."""

import os
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class APIConfig(BaseModel):
    """Configuration for API clients."""

    openrouter_api_key: str = Field(
        default_factory=lambda: os.environ.get("OPENROUTER_API_KEY", "")
    )
    openrouter_base_url: str = Field(
        default_factory=lambda: os.environ.get(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
    )
    image_api_key: str = Field(default_factory=lambda: os.environ.get("IMAGE_API_KEY", ""))
    image_api_base_url: str = Field(
        default_factory=lambda: os.environ.get("IMAGE_API_BASE_URL", "")
    )
    http_timeout: int = Field(default_factory=lambda: int(os.environ.get("HTTP_TIMEOUT", "30")))


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""

    tokens_per_minute: int = Field(
        default_factory=lambda: int(os.environ.get("RATE_LIMIT_TOKENS_PER_MINUTE", "90000"))
    )
    images_per_minute: int = Field(
        default_factory=lambda: int(os.environ.get("RATE_LIMIT_IMAGES_PER_MINUTE", "50"))
    )


class CacheConfig(BaseModel):
    """Configuration for caching."""

    enable_cache: bool = Field(
        default_factory=lambda: os.environ.get("ENABLE_CACHE", "true").lower()
        in ("true", "1", "yes")
    )
    cache_expiry_seconds: int = Field(
        default_factory=lambda: int(os.environ.get("CACHE_EXPIRY_SECONDS", "86400"))
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    log_level: str = Field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))


class Config(BaseModel):
    """Main configuration for the application."""

    api: APIConfig = Field(default_factory=APIConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    default_model: str = Field(
        default_factory=lambda: os.environ.get("DEFAULT_MODEL", "anthropic/claude-3.7-sonnet")
    )
    default_model_params: Dict[str, Any] = Field(default_factory=dict)


@lru_cache
def get_config() -> Config:
    """Get application configuration (cached).

    Returns:
        Config: Application configuration
    """
    config = Config()
    return config


def validate_config() -> Optional[str]:
    """Validate the configuration and return an error message if invalid.

    Returns:
        Optional[str]: Error message if invalid, None if valid
    """
    config = get_config()

    if not config.api.openrouter_api_key:
        return "OPENROUTER_API_KEY environment variable is not set"

    if not config.api.image_api_key:
        return "IMAGE_API_KEY environment variable is not set"

    return None
