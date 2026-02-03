from pydantic import BaseModel, Field


class DurationSettings(BaseModel):
    """
    Settings related to segment duration configuration.

    Attributes:
        minimum (float): The minimum duration (in seconds) for a segment to be considered valid
        maximum (float): The maximum duration (in seconds) for a segment before it should be split.
        hard_limit (float): The hard limit duration (in seconds) for segments; segments longer than this will be forcibly split.
        overlap (float): The duration (in seconds) of overlap between consecutive segments to ensure continuity
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in strategy settings

    minimum: float = Field(
        default=10.0,
        description="The minimum duration (in seconds) for a segment to be considered valid.",
    )

    maximum: float = Field(
        default=15.0,
        description="The maximum duration (in seconds) for a segment before it should be split.",
    )

    hard_limit: float = Field(
        default=30.0,
        description="The hard limit duration (in seconds) for segments; segments longer than this will be forcibly split.",
    )

    overlap: float = Field(
        default=0.5,
        description="The duration (in seconds) of overlap between consecutive segments to ensure continuity.",
    )
