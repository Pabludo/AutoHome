"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Idealista
    idealista_email: str = ""
    idealista_password: str = ""

    # Clientify
    clientify_username: str = ""
    clientify_password: str = ""
    clientify_api_token: str = ""
    clientify_base_url: str = "https://api.clientify.net/v1"

    # Inmovilla
    inmovilla_api_url: str = "https://procesos.inmovilla.com/api/v1"
    inmovilla_api_token: str = ""
    inmovilla_oficina: str = ""
    inmovilla_user: str = ""
    inmovilla_password: str = ""

    # Database
    database_url: str = "sqlite:///data/autohome.db"

    # Pipeline
    pipeline_interval_hours: int = 6
    scraper_delay_min_seconds: int = 3
    scraper_delay_max_seconds: int = 7
    scraper_max_properties_per_session: int = 10

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()
