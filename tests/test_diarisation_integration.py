import math
import os
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest

from minicon.config import Config
from minicon.pipeline import MiniConPipeline


def _write_sine_wave(path: Path, duration: float = 1.0, freq: float = 440.0) -> None:
    sample_rate = 16000
    amplitude = 32767
    frames = int(duration * sample_rate)
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(frames):
            value = int(amplitude * math.sin(2 * math.pi * freq * (i / sample_rate)))
            wav_file.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_DIARISATION_INTEGRATION") != "1",
    reason="Set RUN_DIARISATION_INTEGRATION=1 to run diarisation integration test",
)
def test_diarisation_real_pipeline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("DIARIZATION_AUTH_TOKEN")
    if not token:
        pytest.skip("No HuggingFace token provided")

    try:
        from pyannote.audio import Pipeline as PyannotePipeline  # noqa: F401
    except ImportError:
        pytest.skip("pyannote.audio not installed")

    cfg = Config(
        report_dir_primary=tmp_path / "reports",
        report_dir_secondary=None,
        temp_dir=tmp_path / "temp",
        model_name="tiny",
        openai_api_key_primary="dummy",
        openai_api_key_secondary=None,
        active_openai_key="PRIMARY",
        diarization_model="pyannote/speaker-diarization-3.1",
        diarization_auth_token=token,
        diarization_min_speakers=1,
        diarization_max_speakers=2,
        diarization_enabled=True,
        log_level=20,
    )
    cfg.language = "en"
    cfg.fp16 = False
    cfg.audio_suffix = ".mp3"
    cfg.transcript_suffix = ".txt"
    cfg.report_suffix = ".txt"
    cfg.ensure_dirs()

    pipeline = MiniConPipeline(cfg)

    audio_path = tmp_path / "sample.wav"
    _write_sine_wave(audio_path)

    dummy_result = {
        "text": "hello world",
        "segments": [{"start": 0.0, "end": 0.5, "text": "hello"}],
        "language": "en",
    }
    pipeline._whisper_model = SimpleNamespace(
        transcribe=lambda *args, **kwargs: dummy_result
    )
    monkeypatch.setattr(pipeline, "_ensure_whisper", lambda: None)

    result = pipeline.transcribe(audio_path)

    assert "diarization" in result
    assert isinstance(result["diarization"], list)
    assert any(seg.get("speaker") for seg in result["diarization"])
