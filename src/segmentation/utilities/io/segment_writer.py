from pathlib import Path

from numpy import ndarray
from soundfile import write

from segmentation.exceptions import SegmentWriteError, AudioDataError


def write_segment(output_path: Path, audio: ndarray, sample_rate: int) -> None:
    """
    Writes an audio segment to disk.

    Args:
        output_path (Path): The path where the audio segment will be saved.
        audio (ndarray): The audio data to write.
        sample_rate (int): The sample rate of the audio data.
    Raises:
        SegmentWriteError: If the segment cannot be written to disk.
        AudioDataError: If the audio data is invalid.
    """
    if audio is None or len(audio) == 0:
        raise AudioDataError("Cannot write empty audio segment")

    if sample_rate <= 0:
        raise AudioDataError(f"Invalid sample rate: {sample_rate}")

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise SegmentWriteError(
            str(output_path), f"Cannot create parent directory: {e}"
        ) from e

    try:
        write(output_path, audio, sample_rate)
    except Exception as e:
        raise SegmentWriteError(str(output_path), str(e)) from e
