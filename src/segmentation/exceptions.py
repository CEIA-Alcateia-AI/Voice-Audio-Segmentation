class SegmentationError(Exception):
    """Base exception for all segmentation-related errors."""

    pass


class AudioLoadError(SegmentationError):
    """Raised when audio file cannot be loaded or read."""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load audio file '{file_path}': {reason}")


class AudioFormatError(SegmentationError):
    """Raised when audio format is invalid or unsupported."""

    def __init__(
        self, file_path: str, expected_format: str = None, details: str = None
    ):
        self.file_path = file_path
        self.expected_format = expected_format
        message = f"Invalid audio format for '{file_path}'"
        if expected_format:
            message += f" (expected: {expected_format})"
        if details:
            message += f": {details}"
        super().__init__(message)


class AudioDataError(SegmentationError):
    """Raised when audio data is invalid or corrupted."""

    def __init__(self, details: str):
        self.details = details
        super().__init__(f"Invalid audio data: {details}")


class SegmentWriteError(SegmentationError):
    """Raised when segment cannot be written to disk."""

    def __init__(self, output_path: str, reason: str):
        self.output_path = output_path
        self.reason = reason
        super().__init__(f"Failed to write segment to '{output_path}': {reason}")


class InvalidTimestampError(SegmentationError):
    """Raised when segment timestamps are invalid."""

    def __init__(self, start: float, end: float, reason: str = None):
        self.start = start
        self.end = end
        message = f"Invalid timestamp range [{start}, {end}]"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class StrategyError(SegmentationError):
    """Raised when segmentation strategy encounters an error."""

    def __init__(self, strategy_name: str, reason: str):
        self.strategy_name = strategy_name
        self.reason = reason
        super().__init__(f"Strategy '{strategy_name}' failed: {reason}")


class ConfigurationError(SegmentationError):
    """Raised when configuration or settings are invalid."""

    def __init__(self, setting_name: str, value: any, reason: str):
        self.setting_name = setting_name
        self.value = value
        self.reason = reason
        super().__init__(
            f"Invalid configuration for '{setting_name}' (value: {value}): {reason}"
        )


class OutputDirectoryError(SegmentationError):
    """Raised when output directory cannot be created or accessed."""

    def __init__(self, directory_path: str, reason: str):
        self.directory_path = directory_path
        self.reason = reason
        super().__init__(f"Cannot access output directory '{directory_path}': {reason}")


class ManifestError(SegmentationError):
    """Raised when manifest file cannot be created or is invalid."""

    def __init__(self, manifest_path: str, reason: str):
        self.manifest_path = manifest_path
        self.reason = reason
        super().__init__(f"Manifest error for '{manifest_path}': {reason}")
