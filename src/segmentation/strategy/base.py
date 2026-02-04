from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Tuple

from librosa import load
from numpy import ndarray
from soundfile import write

from segmentation.settings.audio import AudioSettings
from segmentation.settings.duration import DurationSettings
from segmentation.settings.file import FileSettings

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

        output_directory = Path(self.file_settings.output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        timestamps = self.segment_array_to_timestamps(audio)
        segments_data: Dict[str, Path] = {}

        logger.info("Creating %d segments for %s", len(timestamps), original_name)

        for index, (start, end) in enumerate(timestamps):
            start_index = self.seconds_to_samples(start)
            end_index = self.seconds_to_samples(end)

            segment_audio = audio[start_index:end_index]

            filename = self.format_filename(original_name, index)
            output_path = output_directory / filename

            self.write_segment(output_path, segment_audio)

            logger.debug(
                "Segment %d saved: %.2fs - %.2fs -> %s",
                index,
                start,
                end,
                filename,
            )

            segments_data[filename] = output_path

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

        audio = self.load_audio(file_path)
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

        audio = self.load_audio(file_path)
        return self.segment_array_to_files(audio, file_path.stem)

    def format_filename(self, original_name: str, segment_index: int) -> str:
        """
        Formats the filename for a segment based on the naming template.

        Args:
            original_name (str): The original name of the audio file.
            segment_index (int): The index of the segment.
        Returns:
            str: Formatted filename for the segment.
        """
        try:
            file_name = self.file_settings.name_template.format(
                original_name=original_name,
                segment_index=segment_index,
            )
        except KeyError as exc:
            raise ValueError(
                f"Invalid name_template '{self.file_settings.name_template}'. "
                f"Missing placeholder: {exc}"
            ) from exc

        extension = self.file_settings.file_format.value
        return f"{file_name}.{extension}"

    def write_segment(self, output_path: Path, audio: ndarray) -> None:
        """
        Writes an audio segment to disk.
        """
        write(output_path, audio, self.audio_settings.sample_rate_hz)

    def load_audio(self, file_path: Path) -> ndarray:
        """
        Loads audio from a file path.

        Args:
            file_path (Path): Path to the audio file.
        Returns:
            ndarray: Loaded audio array.
        """
        audio, _ = load(
            file_path,
            sr=self.audio_settings.sample_rate_hz,
            mono=(self.audio_settings.channels == 1),
        )

        logger.debug(
            "Loaded audio file %s with shape %s",
            file_path.name,
            audio.shape,
        )

        return audio

    def seconds_to_samples(self, seconds: float) -> int:
        """
        Converts seconds to sample index using rounding to avoid drift.

        Args:
            seconds (float): Time in seconds.
        Returns:
            int: Corresponding sample index.
        """
        return round(seconds * self.audio_settings.sample_rate_hz)
