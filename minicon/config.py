from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import openai
from dotenv import load_dotenv

# Load environment variables from .env file(s)
load_dotenv()
_package_env = Path(__file__).with_name(".env")
if _package_env.exists():
    load_dotenv(_package_env, override=False)


DEFAULT_PRIMARY_REPORT_DIR = Path(r"E:\Projects\Development\text_reports")
DEFAULT_SECONDARY_REPORT_DIR = Path(r"D:\reports")
DEFAULT_TEMP_DIR = Path.cwd() / "yt_temp"


class ConfigError(RuntimeError):
    """Raised when configuration values are invalid or incomplete."""


@dataclass
class Config:
    """Configuration for the MiniCon pipeline.

    - report_dir_primary: main location for generated reports
    - report_dir_secondary: optional secondary mirror location (e.g., D:\\reports)
    - temp_dir: working directory for downloads and intermediates
    - model_name: Whisper model to use (tiny/base/small/medium/large)
    - openai_api_key: OpenAI API key for any OpenAI API calls
    - diarization_model: Optional HuggingFace identifier for speaker diarization
    - diarization_auth_token: Optional auth token for private diarization models
    - diarization_min_speakers / diarization_max_speakers: Bounds used during diarization
    - log_level: Python logging level
    """

    report_dir_primary: Path = DEFAULT_PRIMARY_REPORT_DIR
    report_dir_secondary: Optional[Path] = DEFAULT_SECONDARY_REPORT_DIR
    temp_dir: Path = DEFAULT_TEMP_DIR
    model_name: str = "medium"
    openai_api_key_primary: Optional[str] = None
    openai_api_key_secondary: Optional[str] = None
    active_openai_key: str = "PRIMARY"  # Can be 'PRIMARY' or 'SECONDARY'
    diarization_model: Optional[str] = None
    diarization_auth_token: Optional[str] = None
    diarization_min_speakers: Optional[int] = None
    diarization_max_speakers: Optional[int] = None
    diarization_enabled: bool = False
    language: str = "en"
    fp16: bool = False
    audio_suffix: str = ".mp3"
    transcript_suffix: str = ".txt"
    report_suffix: str = ".txt"
    transcribe_timeout_seconds: Optional[int] = None
    log_level: int = logging.INFO
    _openai_client: Any = field(init=False, default=None)

    @classmethod
    def from_env(cls) -> "Config":
        primary = Path(os.getenv("REPORT_DIR", str(DEFAULT_PRIMARY_REPORT_DIR)))
        secondary_env = os.getenv(
            "SECONDARY_REPORT_DIR", str(DEFAULT_SECONDARY_REPORT_DIR)
        )
        secondary: Optional[Path] = Path(secondary_env) if secondary_env else None
        temp = Path(os.getenv("TEMP_DIR", str(DEFAULT_TEMP_DIR)))
        model = os.getenv("WHISPER_MODEL", "medium")

        primary_key = os.getenv("OPENAI_API_KEY_PRIMARY")
        secondary_key = os.getenv("OPENAI_API_KEY_SECONDARY")
        active_key = os.getenv("ACTIVE_OPENAI_KEY", "PRIMARY")
        diarization_model = os.getenv("DIARIZATION_MODEL")
        diarization_auth = os.getenv("DIARIZATION_AUTH_TOKEN") or os.getenv(
            "HUGGINGFACE_TOKEN"
        )
        diarization_min = os.getenv("DIARIZATION_MIN_SPEAKERS")
        diarization_max = os.getenv("DIARIZATION_MAX_SPEAKERS")
        diarization_flag = os.getenv("MINICON_ENABLE_DIARISATION", "false").lower() in {
            "1",
            "true",
            "yes",
        }

        language = os.getenv("WHISPER_LANGUAGE", "en")
        fp16_env = os.getenv("WHISPER_FP16", "false").lower()
        fp16_value = fp16_env in {"1", "true", "yes"}
        audio_suffix = os.getenv("AUDIO_SUFFIX", ".mp3")
        transcript_suffix = os.getenv("TRANSCRIPT_SUFFIX", ".txt")
        report_suffix = os.getenv("REPORT_SUFFIX", ".txt")
        timeout_env = os.getenv("TRANSCRIBE_TIMEOUT_SECONDS")
        timeout_value = (
            int(timeout_env) if timeout_env and timeout_env.isdigit() else None
        )

        min_speakers = int(diarization_min) if diarization_min else None
        max_speakers = int(diarization_max) if diarization_max else None

        if diarization_flag and not diarization_auth:
            raise ConfigError(
                "Diarisation requested (MINICON_ENABLE_DIARISATION=1) but no "
                "HUGGINGFACE_TOKEN or DIARIZATION_AUTH_TOKEN provided."
            )

        return cls(
            report_dir_primary=primary,
            report_dir_secondary=secondary,
            temp_dir=temp,
            model_name=model,
            openai_api_key_primary=primary_key,
            openai_api_key_secondary=secondary_key,
            active_openai_key=active_key,
            diarization_model=diarization_model,
            diarization_auth_token=diarization_auth,
            diarization_min_speakers=min_speakers,
            diarization_max_speakers=max_speakers,
            diarization_enabled=diarization_flag,
            language=language,
            fp16=fp16_value,
            audio_suffix=audio_suffix,
            transcript_suffix=transcript_suffix,
            report_suffix=report_suffix,
            transcribe_timeout_seconds=timeout_value,
            log_level=logging.INFO,
        )

    def __post_init__(self):
        """Initialize the logger after the object is created."""
        self.log = logging.getLogger(__name__)
        self.log.setLevel(self.log_level)
        self.ensure_dirs()

    def ensure_dirs(self) -> None:
        """Ensure all required directories exist."""
        self.report_dir_primary.mkdir(parents=True, exist_ok=True)
        if self.report_dir_secondary:
            self.report_dir_secondary.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    @property
    def active_api_key(self) -> str:
        """Return the API key selected by ``active_openai_key``.

        Returns:
            str: The active API key string.

        Raises:
            ValueError: If no valid API key is available for the active slot.
        """
        key = (
            self.openai_api_key_primary
            if self.active_openai_key.upper() == "PRIMARY"
            else self.openai_api_key_secondary
        )

        if not key:
            key_name = self.active_openai_key.lower()
            raise ValueError(
                f"No {key_name} OpenAI API key found. "
                f"Please set OPENAI_API_KEY_{self.active_openai_key} in your environment."
            )
        return key

    def switch_api_key(self, key_type: str = "PRIMARY") -> None:
        """Switch between primary and secondary API keys.

        Args:
            key_type: Either 'PRIMARY' or 'SECONDARY'

        Raises:
            ValueError: If key_type is not 'PRIMARY' or 'SECONDARY'
        """
        key_type = key_type.upper()
        if key_type not in ("PRIMARY", "SECONDARY"):
            raise ValueError("key_type must be either 'PRIMARY' or 'SECONDARY'")

        self.active_openai_key = key_type
        self._openai_client = None  # Reset client to force reinitialization
        self.log.info(f"Switched to {key_type} OpenAI API key")

    @property
    def openai_client(self) -> Any:
        """Get or initialize the OpenAI client with the active API key.

        Returns:
            The OpenAI client instance.

        Raises:
            ValueError: If no valid API key is found.
        """
        if self._openai_client is None:
            api_key = self.active_api_key
            self._openai_client = openai.OpenAI(api_key=api_key)

        return self._openai_client
