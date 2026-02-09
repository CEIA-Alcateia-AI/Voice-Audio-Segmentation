from pathlib import Path

from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """
    Manifest model representing the structure of a manifest file for a segmented audio file.

    Attributes:
        original_file (str): The path to the original audio file that was segmented.
        index: int: The index of the segment.
        segment_file (str): The path to the segmented audio file. Empty string if segments
                           were not written to disk (timestamp-only mode).
        start_time (float): The start time of the segment in seconds.
        end_time (float): The end time of the segment in seconds.
        time_to_segment (float): The average time taken to segment per segment in seconds.
            Calculated as total timestamp computation time divided by number of segments.
    """

    original_file: str = Field(
        description="The path to the original audio file that was segmented."
    )

    index: int = Field(description="The index of the segment.")

    segment_file: str = Field(
        description="The path to the segmented audio file. Empty if not written to disk."
    )

    start_time: float = Field(description="The start time of the segment in seconds.")

    end_time: float = Field(description="The end time of the segment in seconds.")

    time_to_segment: float = Field(
        description="The average time taken per segment in seconds. Total segmentation time divided by number of segments."
    )

    def to_json(self) -> str:
        """
        Converts the Manifest instance to a JSON string.

        Returns:
            str: A JSON string representation of the Manifest instance.
        """
        return self.model_dump_json(indent=4)

    def to_json_file(self, file_path: Path) -> None:
        """
        Writes the Manifest instance to a JSON file.

        Args:
            file_path (Path): The path to the JSON file where the manifest will be saved.
        Raises:
            ManifestError: If the manifest cannot be written to the file.
        """
        from segmentation.exceptions import ManifestError

        try:
            with open(file_path, "w", encoding="utf-8") as json_file:
                json_file.write(self.to_json())
        except Exception as e:
            raise ManifestError(str(file_path), str(e)) from e
