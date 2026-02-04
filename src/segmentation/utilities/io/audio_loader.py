from logging import getLogger
from pathlib import Path

from librosa import load
from numpy import ndarray

from segmentation.exceptions import AudioLoadError, AudioFormatError, AudioDataError

logger = getLogger(__name__)


def load_audio(file_path: Path, sample_rate: int, channels: int) -> ndarray:
    """
    Loads audio from a file path.

    Args:
        file_path (Path): Path to the audio file.
        sample_rate (int): Desired sample rate for loading.
        channels (int): Number of audio channels (1 for mono, 2 for stereo).
    Returns:
        ndarray: Loaded audio array.
    Raises:
        AudioLoadError: If the file cannot be loaded.
        AudioFormatError: If the audio format is invalid or unsupported.
        AudioDataError: If the loaded audio data is invalid.
    """
    if not file_path.exists():
        raise AudioLoadError(str(file_path), "File does not exist")

    if not file_path.is_file():
        raise AudioLoadError(str(file_path), "Path is not a file")

    try:
        audio, _ = load(
            file_path,
            sr=sample_rate,
            mono=(channels == 1),
        )
    except Exception as e:
        if "format" in str(e).lower() or "codec" in str(e).lower():
            raise AudioFormatError(str(file_path), details=str(e)) from e
        raise AudioLoadError(str(file_path), str(e)) from e

    if audio is None or len(audio) == 0:
        raise AudioDataError(f"Loaded audio from '{file_path}' is empty")

    if not isinstance(audio, ndarray):
        raise AudioDataError(f"Expected ndarray, got {type(audio).__name__}")

    logger.debug(
        "Loaded audio file %s with shape %s",
        file_path.name,
        audio.shape,
    )
    return audio
