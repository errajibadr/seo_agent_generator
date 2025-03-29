import re
import unicodedata


def normalize_column_name(column_name) -> str:
    """Normalize the column names of a table."""
    # Convert to string and lowercase
    name = str(column_name).lower()

    # Normalize unicode characters (removes accents)
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("utf-8")

    # Replace spaces and remove parentheses
    name = re.sub(r"[\s()]", "_", name)

    # Replace multiple underscores with a single one
    name = re.sub(r"_+", "_", name)

    # Remove leading/trailing underscores
    name = name.strip("_")

    return name
