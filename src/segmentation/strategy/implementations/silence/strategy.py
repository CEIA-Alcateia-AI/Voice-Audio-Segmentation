from logging import getLogger
from typing import List, Optional

from librosa.effects import split
from numpy import ndarray

from segmentation.strategy.base import BaseStrategy, Timestamp
from segmentation.settings.audio import AudioSettings
from segmentation.settings.duration import DurationSettings
from segmentation.settings.file import FileSettings
from segmentation.settings.implementations.silence import SilenceStrategySettings
from segmentation.exceptions import SilenceDetectionError, EmptySegmentationError

logger = getLogger(__name__)


class SilenceStrategy(BaseStrategy):
    """
    Segmentation strategy that detects silence in audio to create segments.

    This strategy analyzes the audio signal to identify periods of silence and
    uses those as boundaries for segmentation. It is particularly effective for
    segmenting speech or music where natural pauses occur.
    """

    def __init__(
        self,
        audio_settings: AudioSettings,
        duration_settings: DurationSettings,
        file_settings: FileSettings,
        silence_settings: Optional[SilenceStrategySettings] = None,
    ) -> None:
        """
        Segmentation strategy that detects silence in audio to create segments.

        Args:
            audio_settings (AudioSettings): Settings related to audio configuration.
            duration_settings (DurationSettings): Settings related to duration configuration.
            file_settings (FileSettings): Settings related to file configuration.
            silence_settings (Optional[SilenceStrategySettings]): Settings specific to silence detection. If None, defaults will be used.
        """
        super().__init__(audio_settings, duration_settings, file_settings)
        self.silence_settings = silence_settings or SilenceStrategySettings()

    def segment_array_to_timestamps(self, audio: ndarray) -> List[Timestamp]:
        """
        Segments the provided audio array into timestamps based on detected silence.

        Args:
            audio (ndarray): The input audio data as a NumPy array.
        Returns:
            List[Timestamp]: A list of (start, end) timestamps in seconds for each segment
        Raises:
            SilenceDetectionError: If silence detection fails.
            EmptySegmentationError: If no valid segments are produced.
        """
        try:
            raw_intervals = split(
                y=audio,
                top_db=self.silence_settings.top_db,
                frame_length=self.silence_settings.frame_length,
                hop_length=self.silence_settings.hop_length,
            )
        except Exception as e:
            raise SilenceDetectionError(str(e)) from e
        merged_intervals = []
        if len(raw_intervals) > 0:
            minimum_gap_samples = int(
                self.silence_settings.minimum_silence_duration
                * self.audio_settings.sample_rate_hz
            )

            current_start, current_end = raw_intervals[0]

            for next_start, next_end in raw_intervals[1:]:
                if next_start - current_end < minimum_gap_samples:
                    current_end = next_end
                else:
                    merged_intervals.append((current_start, current_end))
                    current_start, current_end = next_start, next_end

            merged_intervals.append((current_start, current_end))
        else:
            merged_intervals = []

        segments = [
            {"start": int(start), "end": int(end)} for start, end in merged_intervals
        ]

        result = self._process_raw_segments(segments, len(audio))

        if not result:
            logger.warning(
                "Silence detection produced no valid segments. "
                "Audio may be entirely silent or settings may be too restrictive."
            )
            raise EmptySegmentationError(
                "No valid segments after silence detection and processing. "
                "Try adjusting top_db, minimum_silence_duration, or duration constraints."
            )

        return result
