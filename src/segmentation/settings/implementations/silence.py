from pydantic import BaseModel, Field


class SilenceStrategySettings(BaseModel):
    """
    Settings related to silence detection configuration.

    Attributes:
        top_db (float): The threshold (in decibels) below reference to consider as silence.
        min_silence_duration (float): The minimum duration (in seconds) of silence required to trigger a split.
    """

    model_config = {"extra": "forbid"}

    top_db: float = Field(
        default=30.0,
        description="The threshold (in decibels) below reference to consider as silence. Higher values are more aggressive.",
    )

    minimum_silence_duration: float = Field(
        default=0.5,
        description="The minimum duration (in seconds) of silence required to trigger a split.",
    )

    frame_length: int = Field(
        default=2048,
        description="The number of samples per analysis frame for silence detection.",
    )

    hop_length: int = Field(
        default=512,
        description="The number of samples between successive analysis frames for silence detection.",
    )
