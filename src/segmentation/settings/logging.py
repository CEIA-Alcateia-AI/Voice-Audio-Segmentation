from pydantic import Field

from segmentation.settings.base import BaseSettings


class LoggingSettings(BaseSettings):
    """
    Settings related to logging configuration.

    Attributes:
        level (str): The logging level for the segmentation application.
        format (str): The format for log messages as a string.
    """

    level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="The logging level for the segmentation application.",
    )
    format: str = Field(
        default="console",
        alias="LOG_FORMAT",
        description="The format for log messages as a string.",
    )
