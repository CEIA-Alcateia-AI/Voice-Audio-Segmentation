from pathlib import Path

from segmentation.exceptions import OutputDirectoryError, ConfigurationError


def build_output_directory(
    output_directory: str,
    output_in_subdirectory: bool,
    original_name: str,
) -> Path:
    """
    Builds the output directory path for segmented files.

    Args:
        output_directory (str): The base output directory.
        output_in_subdirectory (bool): Whether to create a subdirectory for each original file.
        original_name (str): The original name of the audio file.
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

    try:
        output_path = Path(output_directory)
    except Exception as e:
        raise OutputDirectoryError(output_directory, f"Invalid path: {e}") from e

    if output_in_subdirectory:
        output_path = output_path / Path(original_name).stem

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
