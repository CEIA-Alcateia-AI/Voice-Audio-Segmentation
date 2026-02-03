from logging import getLogger, WARNING

from segmentation.settings.logging import LoggingSettings


def configure_logging(settings: LoggingSettings) -> None:
    """
    Configures the logging for the segmentation application based on the provided settings.

    Args:
        settings (LoggingSettings): The logging settings to configure the logger.
    """
    segmentation_logger = getLogger("segmentation")
    segmentation_logger.setLevel(settings.level.upper())

    if settings.silence_external_loggers:
        # List of libraries used by the segmentation application whose loggers should be silenced
        external_loggers = []

        for logger in external_loggers:
            getLogger(logger).setLevel(WARNING)
