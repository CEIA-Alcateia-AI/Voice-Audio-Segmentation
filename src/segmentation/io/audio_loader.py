from logging import getLogger
from pathlib import Path

from librosa import load
from numpy import ndarray

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
    """
    audio, _ = load(
        file_path,
        sr=sample_rate,
        mono=(channels == 1),
    )

    logger.debug(
        "Loaded audio file %s with shape %s",
        file_path.name,
        audio.shape,
    )
    return audio
