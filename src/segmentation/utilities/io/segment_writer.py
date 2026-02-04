from pathlib import Path

from numpy import ndarray
from soundfile import write


def write_segment(output_path: Path, audio: ndarray, sample_rate: int) -> None:
    """
    Writes an audio segment to disk.

    Args:
        output_path (Path): The path where the audio segment will be saved.
        audio (ndarray): The audio data to write.
        sample_rate (int): The sample rate of the audio data.
    """
    write(output_path, audio, sample_rate)
