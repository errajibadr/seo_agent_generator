"""Repository for managing keyword data for experiments."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.data.models import KeywordData
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KeywordRepository:
    """Repository for managing keyword data for experiments.

    This class provides methods to load, save, and filter keyword data
    from/to file storage, with a design that can be extended to use database storage.
    """

    def __init__(self, data_dir: Optional[Union[str, Path]] = None):
        """Initialize the keyword repository.

        Args:
            data_dir: Directory for storing keyword data, defaults to src/experiments/data
        """
        if data_dir is None:
            # Default to project structure
            root_dir = Path(__file__).parent.parent.parent.parent
            data_dir = root_dir / "src" / "experiments" / "data"

        self.data_dir = Path(data_dir)
        self.clusters_dir = self.data_dir / "keyword_clusters"

        # Create directories if they don't exist
        self.clusters_dir.mkdir(exist_ok=True, parents=True)

    def save_cluster(
        self, name: str, keywords: List[KeywordData], tags: Optional[List[str]] = None
    ) -> None:
        """Save a keyword cluster to storage.

        Args:
            name: Name of the cluster
            keywords: List of keyword data
            tags: Optional list of tags for the cluster
        """
        cluster_path = self.clusters_dir / f"{name}.json"

        # Create cluster metadata
        cluster_data = {
            "name": name,
            "tags": tags or [],
            "count": len(keywords),
            "keywords": [keyword.model_dump() for keyword in keywords],
        }

        with open(cluster_path, "w") as f:
            json.dump(cluster_data, f, indent=2)

        logger.info(f"Saved keyword cluster: {name} with {len(keywords)} keywords")

    def get_cluster(self, name: str) -> List[KeywordData]:
        """Get a keyword cluster by name.

        Args:
            name: Name of the cluster

        Returns:
            List of keyword data

        Raises:
            FileNotFoundError: If cluster does not exist
        """
        cluster_path = self.clusters_dir / f"{name}.json"

        if not cluster_path.exists():
            raise FileNotFoundError(f"Keyword cluster not found: {name}")

        with open(cluster_path, "r") as f:
            cluster_data = json.load(f)

        return [KeywordData(**keyword_data) for keyword_data in cluster_data["keywords"]]

    def get_cluster_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a keyword cluster.

        Args:
            name: Name of the cluster

        Returns:
            Dictionary with cluster metadata

        Raises:
            FileNotFoundError: If cluster does not exist
        """
        cluster_path = self.clusters_dir / f"{name}.json"

        if not cluster_path.exists():
            raise FileNotFoundError(f"Keyword cluster not found: {name}")

        with open(cluster_path, "r") as f:
            cluster_data = json.load(f)

        # Return only metadata, not the keywords
        return {
            "name": cluster_data["name"],
            "tags": cluster_data["tags"],
            "count": cluster_data["count"],
        }

    def list_clusters(self) -> List[str]:
        """List all available keyword clusters.

        Returns:
            List of cluster names
        """
        cluster_files = self.clusters_dir.glob("*.json")
        return [file.stem for file in cluster_files]

    def filter_clusters_by_tags(self, tags: List[str]) -> List[str]:
        """Filter clusters by tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of cluster names that match the tags
        """
        matching_clusters = []

        for cluster_name in self.list_clusters():
            try:
                metadata = self.get_cluster_metadata(cluster_name)
                # Check if any of the tags match
                if any(tag in metadata["tags"] for tag in tags):
                    matching_clusters.append(cluster_name)
            except Exception as e:
                logger.warning(f"Error processing cluster {cluster_name}: {e}")

        return matching_clusters

    def import_from_csv(
        self, csv_path: Union[str, Path], cluster_name: str, tags: Optional[List[str]] = None
    ) -> List[KeywordData]:
        """Import keyword data from a CSV file and save as a cluster.

        Args:
            csv_path: Path to CSV file
            cluster_name: Name for the new cluster
            tags: Optional list of tags for the cluster

        Returns:
            List of imported keyword data
        """
        from src.data.csv_processor import CSVProcessor

        csv_processor = CSVProcessor(csv_path)
        clusters = csv_processor.read_csv()

        # Get the first cluster from the CSV (or specified one if available)
        if len(clusters) == 0:
            raise ValueError(f"No clusters found in CSV file: {csv_path}")

        # Use the first cluster if the CSV contains multiple
        csv_cluster_name = list(clusters.keys())[0]
        keywords = clusters[csv_cluster_name]

        # Save to our repository
        self.save_cluster(cluster_name, keywords, tags)

        logger.info(f"Imported {len(keywords)} keywords from {csv_path} to cluster {cluster_name}")
        return keywords
