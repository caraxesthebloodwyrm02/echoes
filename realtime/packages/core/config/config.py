from pydantic_settings import BaseSettings
from pathlib import Path

class UnifiedConfig(BaseSettings):
    echoes_root: Path = Path("D:/realtime")
    turbo_root: Path = Path("D:/realtime/turbobookshelf")
    glimpse_root: Path = Path("D:/realtime")

    class Config:
        env_file = ".env"
        extra = "ignore"
