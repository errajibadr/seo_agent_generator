"""Text utilities for the SEO blog generator."""

import math
import re
from typing import Union

from bs4 import BeautifulSoup


def strip_html(html_content: str) -> str:
    """Remove HTML tags from a string and return clean text.

    Args:
        html_content: HTML content to process

    Returns:
        Clean text with HTML tags removed and whitespace normalized
    """
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()
    # Normalize whitespace
    return " ".join(text.split())


def estimate_reading_time(
    content: Union[str, BeautifulSoup],
    words_per_minute: int = 150,
    round_up: bool = True,
) -> int:
    """Estimate reading time in minutes for the provided content.

    Args:
        content: HTML content as string or BeautifulSoup object
        words_per_minute: Average reading speed (default 225 wpm)
        round_up: Whether to round up to nearest minute (default True)

    Returns:
        Estimated reading time in minutes
    """
    # If content is a string, assume it's HTML and strip tags
    if isinstance(content, str):
        text = strip_html(content)
    else:
        text = content.get_text()

    # Count words (split on whitespace)
    word_count = len(text.split())

    # Calculate reading time
    reading_time = word_count / words_per_minute

    # Round up or down based on preference
    if round_up:
        return math.ceil(reading_time)
    return round(reading_time)


def sanitize_filename(name: str) -> str:
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
