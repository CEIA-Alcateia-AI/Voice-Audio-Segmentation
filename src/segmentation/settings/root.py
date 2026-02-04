from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from segmentation.settings.audio import AudioSettings
from segmentation.settings.duration import DurationSettings
from segmentation.settings.file import FileSettings
from segmentation.settings.logging import LoggingSettings

from segmentation.settings.implementations.silence import SilenceStrategySettings


class Settings(BaseSettings):
    """
    Base settings class for segmentation configuration.

    This class can be extended by other settings classes to inherit common configuration.

    Attributes:
        audio (AudioSettings): Settings related to audio configuration.
        duration (DurationSettings): Settings related to duration configuration.
        file (FileSettings): Settings related to file configuration.
        logging (LoggingSettings): Settings related to logging configuration.

        silence_strategy (SilenceStrategySettings): Settings specific to the silence detection segmentation strategy.
    """

    audio: AudioSettings = Field(default_factory=AudioSettings)
    duration: DurationSettings = Field(default_factory=DurationSettings)
    file: FileSettings = Field(default_factory=FileSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Settings for specific segmentation strategies
    silence_strategy: SilenceStrategySettings = Field(
        default_factory=SilenceStrategySettings,
        description="Settings specific to the silence detection segmentation strategy.",
    )

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
