"""Main entry point for the SEO blog generator."""

import argparse
import asyncio
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from src.agents.content_writer import ContentWriter
from src.agents.image_generator import ImageGenerator
from src.config import validate_config
from src.data.csv_processor import CSVProcessor
from src.data.models import BlogArticle, KeywordData
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def process_cluster(
    cluster_name: str,
    cluster_data: List[KeywordData],
    content_writer: ContentWriter,
    image_generator: ImageGenerator,
    output_dir: Path,
) -> Optional[BlogArticle]:
    """Process a single cluster.

    Args:
        cluster_name: Cluster name
        cluster_data: Cluster data
        content_writer: Content writer agent
        image_generator: Image generator agent
        output_dir: Output directory

    Returns:
        Generated blog article or None if failed
    """
    blog_article = None
    try:
        # Generate blog content
        logger.info(f"Generating content for cluster: {cluster_name}")
        blog_article = await content_writer.generate_blog(cluster_name, cluster_data)

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
        logger.error(f"Error processing cluster {cluster_name}: {e}")

        # If we have a blog article but there was an error in later steps,
        # save it to the backup location to prevent content loss
        if blog_article:
            try:
                backup_dir = Path("log/content")
                backup_dir.mkdir(parents=True, exist_ok=True)
                timestamp = int(time.time())
                error_file = (
                    backup_dir / f"{blog_article.slug.replace(' ', '_')}_{timestamp}_error.json"
                )

                with open(error_file, "w", encoding="utf-8") as f:
                    json.dump(blog_article.to_json_dict(), f, ensure_ascii=False, indent=2)
                logger.info(f"Saved failed blog content to {error_file}")
            except Exception as backup_error:
                logger.error(f"Failed to save backup of blog content: {backup_error}")

        return None


async def process_batch(
    keyword_data_dict: dict[str, List[KeywordData]],
    output_dir: Path,
    local_seo: Optional[str] = None,
    max_concurrent: int = 1,
) -> None:
    """Process a batch of clusters.

    Args:
        keyword_data_dict: Dictionary of cluster name to list of keyword data
        output_dir: Output directory
        max_concurrent: Maximum number of concurrent tasks
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    content_writer = ContentWriter(near_me=local_seo)
    image_generator = ImageGenerator()

    # Process in batches to avoid overwhelming APIs
    total = len(keyword_data_dict)
    logger.info(f"Processing {total} Clusters with max {max_concurrent} concurrent tasks")

    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_semaphore(cluster_name: str, cluster_data: List[KeywordData]):
        async with semaphore:
            return await process_cluster(
                cluster_name, cluster_data, content_writer, image_generator, output_dir
            )

    # Create tasks
    tasks = [
        process_with_semaphore(cluster_name, cluster_data)
        for cluster_name, cluster_data in keyword_data_dict.items()
    ]

    # Run tasks and get results
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successes and failures
    successes = sum(1 for r in results if isinstance(r, BlogArticle))
    failures = sum(1 for r in results if r is None or isinstance(r, Exception))

    logger.info(f"Batch processing complete: {successes} successful, {failures} failed")


def merge_keyword_data_dicts(
    dicts_list: List[Dict[str, List[KeywordData]]],
) -> Dict[str, List[KeywordData]]:
    """Merge multiple keyword data dictionaries into one.

    Args:
        dicts_list: List of keyword data dictionaries to merge

    Returns:
        Merged dictionary
    """
    merged_dict = {}
    for data_dict in dicts_list:
        for cluster_name, cluster_data in data_dict.items():
            if cluster_name not in merged_dict:
                merged_dict[cluster_name] = []
            merged_dict[cluster_name].extend(cluster_data)
    return merged_dict


def parse_args():
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Generate SEO blog articles from keyword data")
    parser.add_argument("--input", required=True, help="Input CSV file or directory of CSV files")
    parser.add_argument("--output", required=True, help="Output directory for generated articles")
    parser.add_argument(
        "--batch",
        type=int,
        default=10,
        help="Number of clusters to process randomly (999 to process all clusters)",
    )
    parser.add_argument(
        "--local-seo",
        type=str,
        default=None,
        help="Local SEO keyword to use for the blog",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent tasks",
    )

    return parser.parse_args()


async def async_main():
    """Async main function."""
    # Parse arguments
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    config_error = validate_config()
    if config_error:
        logger.error(f"Configuration error: {config_error}")
        sys.exit(1)

    # Check if input path exists
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect CSV files to process
    csv_to_process = []
    if input_path.is_dir():
        # Find all CSV files in directory
        csv_files = list(input_path.glob("*.csv"))
        if not csv_files:
            logger.error(f"No CSV files found in {input_path}")
            sys.exit(1)
        csv_to_process.extend(csv_files)
        logger.info(f"Found {len(csv_files)} CSV files to process")
    else:
        # Single file
        csv_to_process.append(input_path)
        logger.info(f"Processing single file: {input_path}")

    # Read and process all CSV files
    keyword_data_dicts = []
    for csv_file in csv_to_process:
        logger.info(f"Reading file: {csv_file}")
        try:
            csv_processor = CSVProcessor(csv_file)
            file_keyword_data = csv_processor.read_csv()

            if not file_keyword_data:
                logger.warning(f"No valid keyword data found in {csv_file}")
                continue

            keyword_data_dicts.append(file_keyword_data)

        except Exception as e:
            logger.error(f"Error processing file {csv_file}: {e}")

    # Merge all data dictionaries
    keyword_data_dict = merge_keyword_data_dicts(keyword_data_dicts)

    if not keyword_data_dict:
        logger.error("No valid keyword data found in any CSV files")
        sys.exit(1)

    # Get all cluster names
    all_clusters = list(keyword_data_dict.keys())
    total_clusters = len(all_clusters)
    logger.info(f"Found {total_clusters} clusters across all processed files")

    # Determine how many clusters to process
    if args.batch >= 999 or args.batch >= total_clusters:
        # Process all clusters
        clusters_to_process = all_clusters
        logger.info(f"Processing all {total_clusters} clusters")
    else:
        # Process random clusters without replacement
        clusters_to_process = random.sample(all_clusters, args.batch)
        logger.info(f"Processing {len(clusters_to_process)} randomly selected clusters")

    # Create a new dictionary with only the selected clusters
    selected_data_dict = {
        cluster_name: keyword_data_dict[cluster_name] for cluster_name in clusters_to_process
    }

    # Process selected clusters
    await process_batch(
        selected_data_dict,
        output_path,
        max_concurrent=args.max_concurrent,
    )


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
