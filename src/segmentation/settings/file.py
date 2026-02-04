from enum import StrEnum

from pydantic import BaseModel, Field


class FileType(StrEnum):
    """
    Enumeration of supported file types for segmentation.

    Attributes:
        WAV (str): Waveform Audio File Format.
        MP3 (str): MPEG-1 Audio Layer III.
        FLAC (str): Free Lossless Audio Codec.
        AAC (str): Advanced Audio Coding.
    """

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"

    JSON = "json"  # Added JSON as a file type for manifest files


class FileSettings(BaseModel):
    """
    Settings related to file configuration for segmentation.

    Attributes:
        output_directory (str): The directory where output segmented files will be saved.
        output_in_subdirectories (bool): Whether to save segmented files in subdirectories in the output directory.
        name_template (str): Template for naming segmented files. Use placeholders like {original_name} and {segment_index}.
        file_format (FileType): The file format for the output segmented files (e.g., 'wav', 'mp3').
        generate_manifest (bool): Whether to generate a manifest file for each segmented audio file.
        manifest_name_template (str): Template for naming the manifest file. Use placeholders like {original_name} and {segment_index}.
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in file settings

    output_directory: str = Field(
        default="output",
        description="The directory where output segmented files will be saved.",
    )

    output_in_subdirectories: bool = Field(
        default=True,
        description="Whether to save segmented files in subdirectories in the output directory.",
    )

    name_template: str = Field(
        default="{original_name}_segment_{segment_index}",
        description="Template for naming segmented files. Use placeholders like {original_name} and {segment_index}.",
    )

    file_format: FileType = Field(
        default=FileType.WAV,
        description="The file format for the output segmented files (e.g., 'wav', 'mp3').",
    )

    generate_manifest: bool = Field(
        default=True,
        description="Whether to generate a manifest file for each segmented audio file.",
    )

    manifest_name_template: str = Field(
        default="{original_name}_manifest_{segment_index}",
        description="Template for naming the manifest file. Use placeholders like {original_name} and {segment_index}.",
    )
