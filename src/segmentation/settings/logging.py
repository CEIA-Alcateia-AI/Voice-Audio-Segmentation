from enum import StrEnum

from pydantic import BaseModel, Field


class LogLevel(StrEnum):
    """
    Enumeration of standard logging levels.
    """

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingSettings(BaseModel):
    """
    Settings related to logging configuration.

    Attributes:
        log_level (LogLevel): The logging level for the segmentation application.
        silence_external_loggers (bool): Whether to silence loggers from external libraries.
    """

    model_config = {"extra": "forbid"}  # Forbid extra fields in logging settings

    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="The logging level for the segmentation application.",
    )
    silence_external_loggers: bool = Field(
        default=True,
        description="Whether to silence loggers from external libraries.",
    )
