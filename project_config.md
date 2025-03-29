# Project Configuration (LTM)

*This file contains the stable, long-term context for the project.*
*It should be updated infrequently, primarily when core goals, tech, or patterns change.*

---

## Core Goal

Create an AI Agent that processes keyword data from CSV files and automatically generates SEO-optimized blog articles with accompanying images. The agent will use predefined prompts to create content tailored to specific keywords and their associated metadata.

---

## Tech Stack

* **Language:** Python 3.10+
* **Data Processing:** Pandas, CSV module
* **Data Validation:** Pydantic
* **Image Generation:** API integration with image generation services
* **Content Generation:** Integration with OpenRouter AI or similar LLM services
* **Storage:** Local file system for output (JSON files)
* **Code Structure:** Object-oriented with modular components
* **Testing:** pytest
* **Linting/Formatting:** Ruff

---

## Critical Patterns & Conventions

* **Data Flow:** CSV → Data Validation → Keyword Processing → Content Generation → Image Generation → JSON Output
* **Prompt Management:** Separate prompt templates stored as Python modules
* **Error Handling:** Comprehensive logging and exception handling with graceful failures
* **Batch Processing:** Support for processing multiple keywords in batch mode
* **Caching:** Implement caching for API responses to reduce duplicate calls
* **Configuration:** Use environment variables for API keys and configuration options
* **Output Format:** Structured JSON with HTML content properly escaped

---

## Key Constraints

* **API Rate Limits:** Must handle rate limiting for external API calls
* **Budget Management:** Track and optimize for API usage costs
* **Performance:** Process keywords in parallel where appropriate
* **Extensibility:** Design should allow for easy addition of new prompt templates or output formats
* **Security:** Sensitive API keys must be properly secured and not hardcoded
* **Quality Control:** Implement validation checks for generated content