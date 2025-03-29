# SEO Blog Generator

An AI Agent that processes keyword data from CSV files and automatically generates SEO-optimized blog articles with accompanying images.

## Features

- Processes CSV files with keyword data
- Validates and transforms data with Pydantic models
- Generates SEO-optimized blog content using OpenRouter AI
- Creates images based on alt text descriptions
- Outputs structured JSON files with blog content and image references
- Supports batch processing of multiple keywords
- Implements caching to reduce API calls and costs

## Project Structure

```
seo_blog_generator/
├── src/
│   └── seo_blog_generator/
│       ├── agents/       # Agent components
│       ├── data/         # Data processing
│       ├── prompts/      # Prompt templates
│       ├── services/     # External API clients
│       └── utils/        # Utilities
├── tests/               # Test files
└── examples/            # Example data
```

## Installation

1. Clone the repository
2. Install dependencies with Poetry:

```bash
pip install poetry
poetry install
```

3. Create a `.env` file with your API keys (see `.env.example`)

## Usage

```bash
# Process a single CSV file
poetry run seo-blog-generator --input keywords.csv --output output_dir

# Run in batch mode
poetry run seo-blog-generator --batch --input data_dir --output output_dir
```

## Development

- Use black and isort for code formatting
- Run tests with pytest
- Follow PEP 8 style guidelines 