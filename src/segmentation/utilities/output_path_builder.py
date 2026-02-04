from pathlib import Path
from typing import Optional

from segmentation.exceptions import OutputDirectoryError, ConfigurationError


def build_output_directory(
    output_directory: str,
    output_in_subdirectory: bool,
    output_segment_in_subdirectory: bool,
    original_name: str,
    segment_index: Optional[int] = None,
) -> Path:
    """
    Builds the output directory path for segmented files.

    Args:
        output_directory (str): The base output directory.
        output_in_subdirectory (bool): Whether to create a subdirectory for each original file.
        output_segment_in_subdirectory (bool): Whether to create subdirectories for each segment.
        original_name (str): The original name of the audio file.
        segment_index (Optional[int]): The index of the segment (required if output_segment_in_subdirectory is True).
    Returns:
        Path: The constructed output directory path.
    Raises:
        ConfigurationError: If configuration is invalid.
        OutputDirectoryError: If the directory cannot be created.
    """
    if output_in_subdirectory and original_name is None:
        raise ConfigurationError(
            "output_in_subdirectory",
            True,
            "original_name must be provided when output_in_subdirectory is True",
        )
    
    if output_segment_in_subdirectory and segment_index is None:
        raise ConfigurationError(
            "output_segment_in_subdirectory",
            True,
            "segment_index must be provided when output_segment_in_subdirectory is True",
        )

    try:
        output_path = Path(output_directory)
    except Exception as e:
        raise OutputDirectoryError(output_directory, f"Invalid path: {e}") from e

    # Add audio file subdirectory if requested
    if output_in_subdirectory:
        output_path = output_path / Path(original_name).stem
    
    # Add segment subdirectory if requested
    if output_segment_in_subdirectory:
        output_path = output_path / f"segment_{segment_index}"

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise OutputDirectoryError(str(output_path), f"Permission denied: {e}") from e
    except Exception as e:
        raise OutputDirectoryError(
            str(output_path), f"Cannot create directory: {e}"
        ) from e

    return output_path


def build_path(
    output_directory: Path,
    filename: str,
) -> Path:
    """
    Builds the full output path for an output file.

    Args:
        output_directory (Path): The output directory path.
        filename (str): The filename for the output file.
    Returns:
        Path: The full output path for the output file.
    """
    return output_directory / filename
