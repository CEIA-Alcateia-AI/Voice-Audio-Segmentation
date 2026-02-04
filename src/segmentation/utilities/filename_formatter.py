from segmentation.settings.file import FileType


def format_filename(
    original_name: str, segment_index: int, template: str, file_format: FileType
) -> str:
    """
    Formats the filename for a segment based on the naming template.

    Args:
        original_name (str): The original name of the audio file.
        segment_index (int): The index of the segment.
        template (str): The naming template to use for formatting the filename.
        file_format (FileType): The file format for the output segmented file.
    Returns:
        str: Formatted filename for the segment.
    """
    try:
        file_name = template.format(
            original_name=original_name,
            segment_index=segment_index,
        )
    except KeyError as exception:
        raise ValueError(
            f"Invalid name_template '{template}'. Missing placeholder: {exception}"
        ) from exception

    extension = file_format.value
    return f"{file_name}.{extension}"
