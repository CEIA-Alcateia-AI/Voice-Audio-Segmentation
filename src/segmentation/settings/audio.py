from pydantic import BaseModel, Field


class AudioSettings(BaseModel):
    """
    Settings related to audio configuration.

    Attributes:
        sample_rate_hz (int): The sample rate for audio processing in Hz.
        channels (int): The number of audio channels (1 for mono, 2 for stereo).
        lufs_db (float): The target LUFS (Loudness Units relative to Full Scale) level for audio normalization.
        strict_validation (bool): Whether to enforce strict validation on audio inputs.
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in audio settings

    sample_rate_hz: int = Field(
        default=16000,
        description="The sample rate for audio processing in Hz.",
    )

    channels: int = Field(
        default=1,
        description="The number of audio channels (1 for mono, 2 for stereo).",
    )

    lufs_db: float = Field(
        default=-23.0,
        description="The target LUFS (Loudness Units relative to Full Scale) level for audio normalization.",
    )
