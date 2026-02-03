from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from segmentation.settings.logging import LoggingSettings


class Settings(BaseSettings):
    """
    Base settings class for segmentation configuration.

    This class can be extended by other settings classes to inherit common configuration.

    Attributes:
        logging (LoggingSettings): Settings related to logging configuration.
    """

    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(
        env_prefix="SEGMENTATION_",  # Prefix for environment variables
        env_nested_delimiter="__",  # Delimiter for nested environment variables
        env_file=(
            ".env.segmentation",
            ".env.defaults",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields in environment variables
        validate_assignment=True,  # Validate fields on assignment
        case_sensitive=False,  # Environment variables are case-insensitive
    )
