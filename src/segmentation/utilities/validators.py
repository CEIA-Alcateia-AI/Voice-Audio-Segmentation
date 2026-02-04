from pathlib import Path
from typing import Union

from numpy import ndarray

from segmentation.exceptions import AudioDataError


def validate_audio_array(audio: ndarray) -> None:
    """
    Validates an audio array.

    Args:
        audio: The audio array to validate.
    Raises:
        AudioDataError: If the audio data is invalid.
    """
    if not isinstance(audio, ndarray):
        raise AudioDataError(f"Expected ndarray, got {type(audio).__name__}")

    if audio.ndim == 0:
        raise AudioDataError("Audio array must have at least one dimension")

    if audio is None or len(audio) == 0:
        raise AudioDataError("Audio array is empty")


def validate_audio_input(audio: Union[str, Path, ndarray]) -> tuple[bool, str]:
    """
    Validates the audio input and returns metadata about it.

    Args:
        audio: The input audio data or path to validate.
    Returns:
        tuple: (is_path: bool, input_label: str)
    Raises:
        AudioDataError: If audio data is invalid.
    """
    is_path = isinstance(audio, (str, Path))
    input_label = str(audio) if is_path else "audio array"

    # If not a path, validate the array
    if not is_path:
        validate_audio_array(audio)

    return is_path, input_label
