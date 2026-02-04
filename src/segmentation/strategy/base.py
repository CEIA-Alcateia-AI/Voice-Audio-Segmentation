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

            # Build output directory for this segment
            output_directory = build_output_directory(
                self.file_settings.output_directory,
                self.file_settings.output_in_subdirectory,
                self.file_settings.output_segment_in_subdirectory,
                original_name,
                segment_index=index,
            )

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
                    segment_file=segment_path.as_posix(),
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

    def _process_raw_segments(
        self, segments: List[Dict], audio_length_samples: int
    ) -> List[Timestamp]:
        """
        Processes raw segments by merging short segments and splitting long segments.

        Args:
            segments (List[Dict]): List of segments with 'start' and 'end' keys.
            audio_length_samples (int): The total length of the audio in samples.
        Returns:
            List[Timestamp]: List of processed segments.
        """
        merged_segments = self._merge_short_segments(segments)
        overlapped_segments = self._apply_overlap(merged_segments, audio_length_samples)

        timestamps: List[Timestamp] = []

        for segment in overlapped_segments:
            duration = (
                segment["end"] - segment["start"]
            ) / self.audio_settings.sample_rate_hz

            if duration < self.duration_settings.hard_lower_limit:
                logger.debug(
                    "Discarding segment %.2f - %.2f (%.2fs) as it is below the hard lower limit.",
                    segment["start"] / self.audio_settings.sample_rate_hz,
                    segment["end"] / self.audio_settings.sample_rate_hz,
                    duration,
                )
                continue

            if duration > self.duration_settings.hard_upper_limit:
                logger.warning(
                    "Discarding segment %.2f - %.2f (%.2fs) as it exceeds the hard upper limit.",
                    segment["start"] / self.audio_settings.sample_rate_hz,
                    segment["end"] / self.audio_settings.sample_rate_hz,
                    duration,
                )
                continue

            timestamps.append(
                (
                    segment["start"] / self.audio_settings.sample_rate_hz,
                    segment["end"] / self.audio_settings.sample_rate_hz,
                )
            )

        return timestamps

    def _apply_overlap(
        self, segments: List[Dict], audio_length_samples: int
    ) -> List[Dict]:
        """
        Applies overlap to segments based on the duration settings.

        Args:
            segments (List[Dict]): List of segments with 'start' and 'end' keys.
            audio_length_samples (int): The total length of the audio in samples.
        Returns:
            List[Dict]: List of segments with applied overlap.
        """
        if self.duration_settings.overlap <= 0:
            return segments

        padding_samples = int(
            seconds_to_samples(
                self.duration_settings.overlap / 2, self.audio_settings.sample_rate_hz
            )
        )

        processed_segments = []

        for segment in segments:
            start = max(0, segment["start"] - padding_samples)
            end = min(audio_length_samples, segment["end"] + padding_samples)

            processed_segments.append({"start": start, "end": end})

        return processed_segments

    def _merge_short_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Merges segments that are shorter than the minimum duration specified
        in the settings with adjacent segments.

        Args:
            segments (List[Dict]): List of segments with 'start' and 'end' keys.
        Returns:
            List[Dict]: List of merged segments.
        """
        if not segments:
            return []

        soft_min_samples = int(
            self.duration_settings.soft_lower_limit * self.audio_settings.sample_rate_hz
        )
        hard_max_samples = int(
            self.duration_settings.hard_upper_limit * self.audio_settings.sample_rate_hz
        )

        target_samples = int(
            (
                self.duration_settings.soft_lower_limit
                + self.duration_settings.soft_upper_limit
            )
            / 2
            * self.audio_settings.sample_rate_hz
        )
        
        max_gap_samples = int(
            self.duration_settings.maximum_merge_gap_duration * self.audio_settings.sample_rate_hz
        )

        i = 0
        while i < len(segments):
            current = segments[i]
            duration = current["end"] - current["start"]

            # If the segment is acceptable (above soft limit), move on.
            # (If it's huge, it will be caught by the hard limit filter later)
            if duration >= soft_min_samples:
                i += 1
                continue

            # Segment is too short (undesired). Evaluate merging options.
            left_segment = segments[i - 1] if i > 0 else None
            right_segment = segments[i + 1] if i < len(segments) - 1 else None

            can_merge_left = False
            score_left = float("inf")

            if left_segment:
                gap = current["start"] - left_segment["end"]
                new_duration = current["end"] - left_segment["start"]
                if new_duration <= hard_max_samples and gap <= max_gap_samples:
                    can_merge_left = True
                    score_left = abs(new_duration - target_samples)

            can_merge_right = False
            score_right = float("inf")

            if right_segment:
                gap = right_segment["start"] - current["end"]
                new_duration = right_segment["end"] - current["start"]
                if new_duration <= hard_max_samples and gap <= max_gap_samples:
                    can_merge_right = True
                    score_right = abs(new_duration - target_samples)

            if not can_merge_left and not can_merge_right:
                logger.debug(
                    "Segment at index %d is short but unmergeable. Keeping for filter.",
                    i,
                )
                i += 1
                continue

            # Prefer the merge that gets us closer to the target duration
            if can_merge_left and (not can_merge_right or score_left <= score_right):
                # Merge Left: Extend previous segment to cover current
                logger.debug("Merging segment %d LEFT into %d", i, i - 1)
                left_segment["end"] = current["end"]
                segments.pop(i)
                # Decrement i to re-evaluate the newly grown previous segment
                # (It might still be short, or now eligible for another merge)
                i -= 1

            elif can_merge_right:
                # Merge Right: Extend right segment to cover current start
                logger.debug("Merging segment %d RIGHT into %d", i, i + 1)
                right_segment["start"] = current["start"]
                segments.pop(i)
                # Do NOT increment i. 'right_segment' has shifted into position 'i'.
                # We stay here to evaluate this new, larger segment.
                continue

            # Ensure we don't loop infinitely in edge cases
            i = max(0, i)

        return segments
