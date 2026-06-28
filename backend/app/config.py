from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Google Gemini
    gemini_api_key: str = ""
    
    # App config
    max_upload_size_mb: int = 50
    allowed_origins: list[str] = ["http://localhost:5173"]
    model_storage_path: str = "./models"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
