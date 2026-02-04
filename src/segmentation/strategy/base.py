from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Tuple

from numpy import ndarray


from segmentation.exceptions import InvalidTimestampError, StrategyError
from segmentation.settings.audio import AudioSettings
from segmentation.settings.duration import DurationSettings
from segmentation.settings.file import FileSettings, FileType
from segmentation.utilities.filename_formatter import format_filename
from segmentation.utilities.io.audio_loader import load_audio
from segmentation.utilities.io.segment_writer import write_segment
from segmentation.utilities.manifest_builder import Manifest
from segmentation.utilities.math.time_conversion import seconds_to_samples
from segmentation.utilities.output_path_builder import (
    build_output_directory,
    build_path,
)

logger = getLogger(__name__)

Timestamp = Tuple[float, float]


class BaseStrategy(ABC):
    def __init__(
        self,
        audio_settings: AudioSettings,
        duration_settings: DurationSettings,
        file_settings: FileSettings,
    ) -> None:
        """
        Base class for segmentation strategies.

        Args:
            audio_settings (AudioSettings): Settings related to audio configuration.
            duration_settings (DurationSettings): Settings related to duration configuration.
            file_settings (FileSettings): Settings related to file configuration.
        """
        self.audio_settings = audio_settings
        self.duration_settings = duration_settings
        self.file_settings = file_settings

        logger.debug("Initialized %s strategy", self.__class__.__name__)

    @abstractmethod
    def segment_array_to_timestamps(self, audio: ndarray) -> List[Timestamp]:
        """
        Abstract method to segment an audio array into timestamps.

        Args:
            audio (ndarray): The input audio array.
        Returns:
            List[Timestamp]: A list of (start, end) timestamps in seconds.
        """
        ...

    def segment_array_to_files(
        self, audio: ndarray, original_name: str
    ) -> Dict[str, Path]:
        """
        Finds timestamps for a given array and writes segments to files.

        Args:
            audio (ndarray): The input audio array.
            original_name (str): The original name of the audio file (used for naming segments).
        Returns:
            Dict[str, Path]: Mapping of segment filenames to their file paths.
        """
        logger.info("Processing timestamps for array with shape %s", audio.shape)

        output_directory = build_output_directory(
            self.file_settings.output_directory,
            self.file_settings.output_in_subdirectories,
            original_name,
        )

        try:
            timestamps = self.segment_array_to_timestamps(audio)
        except Exception as e:
            raise StrategyError(
                self.__class__.__name__, f"Failed to generate timestamps: {e}"
            ) from e

        segments_data: Dict[str, Path] = {}

        logger.info("Creating %d segments for %s", len(timestamps), original_name)

        for index, (start, end) in enumerate(timestamps):
            # Validate timestamp
            if start < 0 or end < 0:
                raise InvalidTimestampError(start, end, "Timestamps cannot be negative")
            if start >= end:
                raise InvalidTimestampError(
                    start, end, "Start time must be before end time"
                )
            if end > len(audio) / self.audio_settings.sample_rate_hz:
                raise InvalidTimestampError(
                    start, end, "End time exceeds audio duration"
                )

            start_index = seconds_to_samples(start, self.audio_settings.sample_rate_hz)
            end_index = seconds_to_samples(end, self.audio_settings.sample_rate_hz)

            segment_audio = audio[start_index:end_index]

            segment_filename = format_filename(
                original_name,
                index,
                self.file_settings.name_template,
                self.file_settings.file_format,
            )

            manifest_filename = format_filename(
                original_name,
                index,
                self.file_settings.manifest_name_template,
                FileType.JSON,
            )

            segment_path = build_path(output_directory, segment_filename)
            manifest_path = build_path(output_directory, manifest_filename)

            write_segment(
                segment_path, segment_audio, self.audio_settings.sample_rate_hz
            )

            if self.file_settings.generate_manifest:
                manifest = Manifest(
                    original_file=original_name,
                    index=index,
                    segment_file=str(segment_path),
                    start_time=start,
                    end_time=end,
                )
                manifest.to_json_file(manifest_path)

            logger.debug(
                "Segment %d saved: %.2fs - %.2fs -> %s",
                index,
                start,
                end,
                segment_filename,
            )

            segments_data[segment_filename] = segment_path

            # Explicitly delete segment_audio to free memory before processing the next segment
            del segment_audio

        return segments_data

    def segment_file_to_timestamps(self, file_path: Path) -> List[Timestamp]:
        """
        Finds timestamps for a given file.

        Args:
            file_path (Path): Path to the audio file.
        Returns:
            List[Timestamp]: A list of (start, end) timestamps.
        """
        logger.info("Processing timestamps for %s", file_path.name)

        audio = load_audio(
            file_path, self.audio_settings.sample_rate_hz, self.audio_settings.channels
        )
        return self.segment_array_to_timestamps(audio)

    def segment_file_to_files(self, file_path: Path) -> Dict[str, Path]:
        """
        Segments a file into multiple files based on timestamps.

        Args:
            file_path (Path): Path to the audio file.
        Returns:
            Dict[str, Path]: Mapping of segment filenames to their file paths.
        """
        logger.info("Processing file segmentation for %s", file_path.name)

        audio = load_audio(
            file_path, self.audio_settings.sample_rate_hz, self.audio_settings.channels
        )
        return self.segment_array_to_files(audio, file_path.stem)
