"""
Application configuration module.

Loads and validates environment variables using pydantic-settings.
Provides a single, type-safe settings object used throughout the application.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables.

    All configuration values are read from the .env file at startup
    and validated by Pydantic. This ensures type safety and a single
    source of truth for configuration.
    """

    # Application metadata
    APP_NAME: str = "Local RAG System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database connection settings
    DB_SERVER: str
    DB_NAME: str
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_TRUSTED_CONNECTION: str = "yes"
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""

    # Tells pydantic-settings to read from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        """
        Construct the SQLAlchemy database connection URL.

        Builds the connection string differently depending on whether
        Windows Authentication (trusted connection) or SQL Server
        Authentication (username/password) is used.

        Returns:
            str: The fully-formed SQLAlchemy connection URL for MS SQL Server.
        """
        driver = self.DB_DRIVER.replace(" ", "+")

        if self.DB_TRUSTED_CONNECTION.lower() == "yes":
            # Windows Authentication — no username/password needed
            return (
                f"mssql+pyodbc://@{self.DB_SERVER}/{self.DB_NAME}"
                f"?driver={driver}&trusted_connection=yes"
            )

        # SQL Server Authentication — username and password required
        return (
            f"mssql+pyodbc://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_SERVER}/{self.DB_NAME}?driver={driver}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached instance of the application settings.

    The @lru_cache decorator ensures the Settings object is created only
    once and reused across the application, avoiding repeated .env reads.

    Returns:
        Settings: The singleton settings instance.
    """
    return Settings()


# A convenient module-level settings instance
settings = get_settings()