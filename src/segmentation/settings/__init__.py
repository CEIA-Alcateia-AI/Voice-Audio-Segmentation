from segmentation.settings.base import BaseSettings
from segmentation.settings.logging import LoggingSettings

class Settings(BaseSettings):
    """
    Main settings class for segmentation configuration.

    Expand this class with additional settings as needed.

    Attributes:
        logging (LoggingSettings): Settings related to logging configuration.
    """
    logging: LoggingSettings = LoggingSettings()

__all__ = ["Settings"]