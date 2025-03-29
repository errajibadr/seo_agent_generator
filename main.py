"""Main entry point for the SEO blog generator."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from src.agents.content_writer import ContentWriter
from src.agents.image_generator import ImageGenerator
from src.config import get_config, validate_config
from src.data.csv_processor import CSVProcessor
from src.data.models import BlogArticle, KeywordData
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def process_keyword(
    keyword_data: KeywordData,
    content_writer: ContentWriter,
    image_generator: ImageGenerator,
    output_dir: Path,
) -> Optional[BlogArticle]:
    """Process a single keyword.

    Args:
        keyword_data: Keyword data
        content_writer: Content writer agent
        image_generator: Image generator agent
        output_dir: Output directory

    Returns:
        Generated blog article or None if failed
    """
    try:
        # Generate blog content
        logger.info(f"Generating content for keyword: {keyword_data.keyword}")
        blog_article = await content_writer.generate_blog(keyword_data)

        # Generate images
        logger.info(f"Generating images for blog: {blog_article.title}")
        blog_article = await image_generator.generate_images(blog_article)

        # Save the article to disk
        output_file = output_dir / f"{blog_article.slug}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(blog_article.to_json_dict(), f, ensure_ascii=False, indent=2)

        logger.info(f"Successfully saved article to {output_file}")

        return blog_article

    except Exception as e:
        logger.error(f"Error processing keyword {keyword_data.keyword}: {e}")
        return None


async def process_batch(
    keyword_data_list: List[KeywordData],
    output_dir: Path,
    max_concurrent: int = 3,
) -> None:
    """Process a batch of keywords.

    Args:
        keyword_data_list: List of keyword data
        output_dir: Output directory
        max_concurrent: Maximum number of concurrent tasks
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create agents
    config = get_config()
    content_writer = ContentWriter()
    image_generator = ImageGenerator()

    # Process in batches to avoid overwhelming APIs
    total = len(keyword_data_list)
    logger.info(f"Processing {total} keywords with max {max_concurrent} concurrent tasks")

    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(kw_data):
        async with semaphore:
            return await process_keyword(kw_data, content_writer, image_generator, output_dir)

    # Create tasks
    tasks = [process_with_semaphore(kw_data) for kw_data in keyword_data_list]

    # Run tasks and get results
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successes and failures
    successes = sum(1 for r in results if isinstance(r, BlogArticle))
    failures = sum(1 for r in results if r is None or isinstance(r, Exception))

    logger.info(f"Batch processing complete: {successes} successful, {failures} failed")


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Generate SEO blog articles from keyword data")
    parser.add_argument("--input", required=True, help="Input CSV file or directory for batch mode")
    parser.add_argument("--output", required=True, help="Output directory for generated articles")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Enable batch mode (process a directory of CSV files)",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent tasks in batch mode",
    )

    return parser.parse_args()


async def async_main():
    """Async main function."""
    # Parse arguments
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate config
    # config_error = validate_config()
    # if config_error:
    #     logger.error(f"Configuration error: {config_error}")
    #     sys.exit(1)

    # Check if input path exists
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    if args.batch:
        # Batch mode
        if not input_path.is_dir():
            logger.error("Batch mode requires input to be a directory")
            sys.exit(1)

        # Get all CSV files in directory
        csv_files = list(input_path.glob("*.csv"))
        if not csv_files:
            logger.error(f"No CSV files found in {input_path}")
            sys.exit(1)

        # Process each CSV file
        logger.info(f"Found {len(csv_files)} CSV files to process")

        for csv_file in csv_files:
            logger.info(f"Processing file: {csv_file}")

            try:
                # Read CSV
                csv_processor = CSVProcessor(csv_file)
                keyword_data_list = csv_processor.read_csv()

                if not keyword_data_list:
                    logger.warning(f"No valid keyword data found in {csv_file}")
                    continue

                # Generate articles for this CSV
                file_output_dir = output_path / csv_file.stem
                await process_batch(
                    keyword_data_list, file_output_dir, max_concurrent=args.max_concurrent
                )

            except Exception as e:
                logger.error(f"Error processing file {csv_file}: {e}")
    else:
        try:
            # Read CSV
            csv_processor = CSVProcessor(input_path)
            keyword_data_list = csv_processor.read_csv()
            keyword_data_list_ibis = csv_processor.read_csv_ibis()

            if not keyword_data_list:
                logger.error("No valid keyword data found in CSV")
                sys.exit(1)

            # Process keywords
            await process_batch(keyword_data_list, output_path, max_concurrent=args.max_concurrent)

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        # Configure and run async loop
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
