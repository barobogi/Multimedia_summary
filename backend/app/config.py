"""Configuration management for the application"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Keys
    anthropic_api_key: str
    github_token: str

    # Gmail
    gmail_user: str
    gmail_refresh_token: Optional[str] = None
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None

    # GitHub
    github_repo: str = "barobogi/Daily_for_Barobogi"
    github_username: str = "barobogi"

    # Drive (OneDrive/Google Drive)
    drive_type: str = "onedrive"  # 'onedrive' or 'google'
    drive_folder_id: Optional[str] = None
    drive_refresh_token: Optional[str] = None

    # Application
    debug: bool = False
    port: int = 8000
    workers: int = 2
    log_level: str = "INFO"

    # API Configuration
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens_summary: int = 2000
    max_tokens_analysis: int = 1000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()  # type: ignore
