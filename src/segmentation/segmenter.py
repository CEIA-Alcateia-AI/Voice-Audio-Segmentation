from logging import getLogger
from pathlib import Path
from typing import Any, Union, Optional

from numpy import ndarray

from segmentation.settings.root import Settings as SegmentationSettings
from segmentation.strategy.base import BaseStrategy as SegmentationStrategy

logger = getLogger(__name__)


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
    ) -> Any:
        """
        Segments the provided audio input and optionally writes the segments to files.

        Args:
            audio (Union[str, Path, ndarray]): The input audio data or path to the audio file.
            output_to_file (bool): Whether to write the segmented files to disk.

        Returns:
            Any: A dictionary of file paths if output_to_file is True,
                 or a list of timestamps if False.
        """
        is_path = isinstance(audio, (str, Path))
        input_label = str(audio) if is_path else "audio array"

        if output_to_file:
            logger.info("Segmenting %s to files.", input_label)
            if is_path:
                segments = self.strategy.segment_file_to_files(Path(audio).resolve())
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
