from pydantic_settings import BaseSettings as ModelSettings, SettingsConfigDict


class BaseSettings(ModelSettings):
    """
    Base settings class for segmentation configuration.
    """

    model_config = SettingsConfigDict(
        env_file=(
            ".env.segmentation.defaults",  # Load the library defaults first
            ".env.segmentation",  # Load the library overrides second
            ".env.defaults",  # Load the project defaults third
            ".env",  # Load the project overrides last
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True,
    )
