"""Test configuration and shared fixtures."""

import warnings


def pytest_configure(config):
    """Configure pytest."""
    # Filter out the pkg_resources deprecation warning from textstat
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message="pkg_resources is deprecated as an API.*",
    )
