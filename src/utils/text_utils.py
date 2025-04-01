"""Text utilities for the SEO blog generator."""

import math
import re
import unicodedata
from typing import Optional, Union

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


def slugify(
    text: str,
    max_length: int = 80,
    word_separator: str = "-",
    allow_unicode: bool = False,
    lowercase: bool = True,
) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: The text to convert to a slug
        max_length: Maximum length of the slug (default: 80)
        word_separator: Character to use for word separation (default: "-")
        allow_unicode: Whether to allow Unicode characters (default: False)
        lowercase: Whether to convert to lowercase (default: True)

    Returns:
        URL-friendly slug string

    Example:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("Héllo Wörld")
        'hello-world'
        >>> slugify("Hello World", word_separator="_")
        'hello_world'
    """
    text = str(text)

    if lowercase:
        text = text.lower()

    if not allow_unicode:
        # Convert to ASCII, replacing accented characters with their non-accented equivalents
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")
    else:
        # Normalize unicode characters but keep them
        text = unicodedata.normalize("NFKC", text)

    # Replace any non-word character (except hyphens) with spaces
    text = re.sub(r"[^\w\s-]", " ", text)

    # Replace all spaces and hyphens with the word separator
    text = re.sub(r"[-\s]+", word_separator, text)

    # Remove word separators from start and end
    text = text.strip(word_separator)

    # Enforce max length while avoiding cutting words in the middle
    if len(text) > max_length:
        words = text.split(word_separator)
        result = []
        current_length = 0

        for word in words:
            # +1 for the word separator
            if current_length + len(word) + 1 <= max_length:
                result.append(word)
                current_length += len(word) + 1
            else:
                break

        text = word_separator.join(result)

    return text
