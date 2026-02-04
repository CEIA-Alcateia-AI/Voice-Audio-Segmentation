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


class FileSettings(BaseModel):
    """
    Settings related to file configuration for segmentation.

    Attributes:
        input_directory (str): The directory where input audio files are located.
        output_directory (str): The directory where output segmented files will be saved.
        name_template (str): Template for naming segmented files. Use placeholders like {original_name} and {segment_index}.
        file_format (FileType): The file format for the output segmented files (e.g.,
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in file settings

    output_directory: str = Field(
        default="output",
        description="The directory where output segmented files will be saved.",
    )

    name_template: str = Field(
        default="{original_name}_segment_{segment_index}",
        description="Template for naming segmented files. Use placeholders like {original_name} and {segment_index}.",
    )

    file_format: FileType = Field(
        default=FileType.WAV,
        description="The file format for the output segmented files (e.g., 'wav', 'mp3').",
    )
