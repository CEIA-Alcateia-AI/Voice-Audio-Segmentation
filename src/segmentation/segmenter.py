from logging import getLogger
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

from numpy import ndarray

from segmentation.exceptions import SegmentationError
from segmentation.settings.root import Settings as SegmentationSettings
from segmentation.strategy.base import BaseStrategy as SegmentationStrategy
from segmentation.utilities.validators import validate_audio_input

logger = getLogger(__name__)

# Type aliases for better readability
Timestamp = Tuple[float, float]
SegmentResult = Union[Dict[str, Path], List[Timestamp]]


class Segmenter:
    """
    Class responsible for segmenting audio files based on a given strategy and settings.
    """

    def __init__(
        self,
        strategy: SegmentationStrategy,
        settings: Optional[SegmentationSettings] = None,
    ) -> None:
        """
        Initializes the Segmenter with a segmentation strategy and optional settings.

        Args:
            strategy (SegmentationStrategy): The segmentation strategy to use.
            settings (Optional[SegmentationSettings]): The configuration settings for segmentation. If None, defaults to environment-based Settings.
        """
        self.strategy = strategy
        self.settings = settings or SegmentationSettings()

    def segment(
        self, audio: Union[str, Path, ndarray], output_to_file: bool = True
    ) -> SegmentResult:
        """
        Segments the provided audio input and optionally writes the segments to files.

        Args:
            audio (Union[str, Path, ndarray]): The input audio data or path to the audio file.
            output_to_file (bool): Whether to write the segmented files to disk.
        Returns:
            SegmentResult: A dictionary mapping segment filenames to file paths if
                          output_to_file is True, or a list of (start, end) timestamps
                          in seconds if False.
        Raises:
            AudioDataError: If audio data is invalid or malformed.
            AudioLoadError: If audio file cannot be loaded.
            SegmentWriteError: If segments cannot be written to disk.
            InvalidTimestampError: If generated timestamps are invalid.
            StrategyError: If the segmentation strategy fails.
            SegmentationError: For any other segmentation-related errors.
        """
        is_path, input_label = validate_audio_input(audio)

        try:
            if output_to_file:
                logger.info("Segmenting %s to files.", input_label)
                if is_path:
                    segments = self.strategy.segment_file_to_files(
                        Path(audio).resolve()
                    )
                else:
                    segments = self.strategy.segment_array_to_files(
                        audio, original_name="array_input"
                    )
            else:
                logger.info("Segmenting %s to timestamps.", input_label)
                if is_path:
                    segments = self.strategy.segment_file_to_timestamps(
                        Path(audio).resolve()
                    )
                else:
                    segments = self.strategy.segment_array_to_timestamps(audio)

            logger.info(
                "Segmentation complete. Generated %d items for %s.",
                len(segments),
                input_label,
            )

            return segments
        except SegmentationError:
            # Re-raise our domain exceptions
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise SegmentationError(f"Unexpected error during segmentation: {e}") from e
