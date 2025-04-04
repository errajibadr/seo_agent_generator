"""OpenRouter AI service for content generation."""

import json
import time
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import Config, get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterService:
    """Service for interacting with the OpenRouter API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        """Initialize the OpenRouter service.

        Args:
            api_key: API key for OpenRouter (defaults to config value)
            base_url: Base URL for OpenRouter API (defaults to config value)
        """
        self.config = config or get_config()
        self.api_key = api_key or self.config.api.openrouter_api_key
        self.base_url = base_url or self.config.api.openrouter_base_url

        # Properties
        self.default_model = self.config.default_model
        self.timeout = self.config.api.http_timeout
        self.temperature = self.config.default_model_params.get("temperature", 0.7)
        self.max_tokens = self.config.default_model_params.get("max_tokens", 4000)
        self.frequency_penalty = self.config.default_model_params.get("frequency_penalty", 0.0)
        self.presence_penalty = self.config.default_model_params.get("presence_penalty", 0.0)
        self.stop_sequences = self.config.default_model_params.get("stop_sequences", [])
        self.top_p = self.config.default_model_params.get("top_p", 1.0)

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _make_api_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make an API request to OpenRouter.

        Args:
            endpoint: API endpoint
            payload: Request payload
            model: Model to use (defaults to default_model)

        Returns:
            API response
        """
        url = f"{self.base_url}/{endpoint}"

        # Add model to payload if not already set
        if "model" not in payload:
            payload["model"] = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://seo-blog-generator.example.com",  # Replace with your site
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Handle rate limiting
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", "5"))
                logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                raise
            raise
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise

    async def generate_content(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate content using the OpenRouter API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model to use (defaults to default_model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Generated content
        """
        messages = []

        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            # "top_p": self.top_p,
            # "frequency_penalty": self.frequency_penalty,
            # "presence_penalty": self.presence_penalty,
            # "stop_sequences": self.stop_sequences,
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        logger.info(f"Generating content with model: {model or self.default_model}")

        response = await self._make_api_request("chat/completions", payload, model)

        try:
            content = response["choices"][0]["message"]["content"]
            logger.info("Content generation successful")
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing response: {e}")
            logger.error(f"Response: {json.dumps(response)}")
            raise ValueError("Invalid response from API")

    async def extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from a response string.

        Args:
            content: Response string that may contain JSON

        Returns:
            Extracted JSON as a dictionary
        """
        try:
            # Try to parse the entire string as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # Find JSON in the response
            json_start = content.find("{")
            json_end = content.rfind("}")

            if json_start >= 0 and json_end >= 0:
                json_content = content[json_start : json_end + 1]
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from content")
                    logger.debug(f"Content: {content}")

            # If no valid JSON found, return empty dict
            return {}
