from pydantic import BaseModel, Field


class DurationSettings(BaseModel):
    """
    Settings related to segment duration configuration.

    Attributes:
        soft_lower_limit (float): The desired minimum duration (in seconds) for a segment to be considered valid
        soft_upper_limit (float): The desired maximum duration (in seconds) for a segment before it should be split.
        hard_lower_limit (float): The hard lower limit duration (in seconds) for segments; segments shorter than this may be merged.
        hard_upper_limit (float): The hard upper limit duration (in seconds) for segments; segments longer than this will be forcibly split.
        overlap (float): The duration (in seconds) of overlap between consecutive segments to ensure continuity
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in strategy settings

    soft_lower_limit: float = Field(
        default=10.0,
        description="The desired minimum duration (in seconds) for a segment to be considered valid.",
    )

    soft_upper_limit: float = Field(
        default=15.0,
        description="The desired maximum duration (in seconds) for a segment before it should be split.",
    )

    hard_lower_limit: float = Field(
        default=5.0,
        description="The hard lower limit duration (in seconds) for segments; segments shorter than this may be merged or discarded.",
    )

    hard_upper_limit: float = Field(
        default=30.0,
        description="The hard upper limit duration (in seconds) for segments; segments longer than this will be forcibly split.",
    )

    overlap: float = Field(
        default=0.5,
        description="The duration (in seconds) of overlap between consecutive segments to ensure continuity.",
    )

    maximum_merge_gap_duration: float = Field(
        default=1.0,
        description="The maximum gap (in seconds) between segments that allows merging. If the silence between two segments exceeds this, they won't be merged.",
    )
