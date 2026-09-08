from pathlib import Path
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CURRENT_DIR.parent.parent
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=(
            str(_REPO_ROOT / ".env"),
            str(_BACKEND_DIR / ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/fact_ledger"
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY_2", "GEMINI_API_KEY-2"),
    )
    GEMINI_API_KEY_3: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY_3", "GEMINI_API_KEY-3"),
    )
    CHROMA_MODE: str = "persistent"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_PREFIX: str = "fact_ledger"
    CHROMA_PERSISTENT_PATH: str = "chroma_data"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def gemini_api_keys(self) -> list[str]:
        """Return configured Gemini keys in priority order without duplicates."""
        return list(
            dict.fromkeys(
                key.strip()
                for key in (
                    self.GEMINI_API_KEY,
                    self.GEMINI_API_KEY_2,
                    self.GEMINI_API_KEY_3,
                )
                if key and key.strip()
            )
        )


settings = Settings()
