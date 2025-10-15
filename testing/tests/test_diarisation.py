# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
from minicon.config import Config
from minicon.pipeline import MiniConPipeline


@pytest.fixture()
def base_config(tmp_path: Path) -> Config:
    cfg = Config(
        report_dir_primary=tmp_path / "reports",
        report_dir_secondary=None,
        temp_dir=tmp_path / "temp",
        model_name="tiny",
        openai_api_key_primary="test-key",
        openai_api_key_secondary=None,
        active_openai_key="PRIMARY",
        diarization_model=None,
        diarization_auth_token="fake-token",
        diarization_min_speakers=None,
        diarization_max_speakers=None,
        diarization_enabled=False,
        log_level=logging.INFO,
    )
    cfg.language = "en"
    cfg.fp16 = False
    cfg.audio_suffix = ".mp3"
    cfg.transcript_suffix = ".txt"
    cfg.report_suffix = ".txt"
    cfg.ensure_dirs()
    return cfg


def test_diarization_stays_disabled_without_token(base_config: Config) -> None:
    base_config.diarization_auth_token = None
    pipe = MiniConPipeline(base_config)
    pipe.enable_diarization(True)
    assert pipe._diarization_enabled is False


def test_transcribe_provides_placeholder_speaker_when_diarizer_missing(
    base_config: Config, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pipe = MiniConPipeline(base_config)
    pipe._diarization_import_error = None
    pipe._diarization_failed = False
    pipe._diarization_enabled = True

    monkeypatch.setattr(pipe, "_ensure_whisper", lambda: None)

    monkeypatch.setattr(pipe, "_ensure_diarizer", lambda: False)

    dummy_result = {
        "text": "hello world",
        "segments": [{"start": 0.0, "end": 1.0, "text": "hello world"}],
        "language": "en",
    }
    pipe._whisper_model = SimpleNamespace(
        transcribe=lambda *args, **kwargs: dummy_result
    )

    audio_path = base_config.temp_dir / "sample.mp3"
    audio_path.write_text("dummy")

    result = pipe.transcribe(audio_path)
    diarization = result.get("diarization")
    if diarization:
        assert diarization[0]["speaker"] == "SPEAKER_00"
    else:
        assert pipe._diarization_enabled is False


def test_transcribe_uses_mocked_diarizer_labels(
    base_config: Config, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class DummyDiarization:
        def itertracks(self, yield_label: bool = True):
            yield (SimpleNamespace(start=0.0, end=1.0), None, "SPEAKER_DI")

    class DummyPipeline:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def __call__(self, *args, **kwargs):
            return DummyDiarization()

    fake_module = types.SimpleNamespace(Pipeline=DummyPipeline)
    monkeypatch.setitem(
        sys.modules, "pyannote", types.SimpleNamespace(audio=fake_module)
    )
    monkeypatch.setitem(sys.modules, "pyannote.audio", fake_module)

    base_config.diarization_model = "dummy/model"
    base_config.diarization_auth_token = "fake-token"

    pipe = MiniConPipeline(base_config)
    pipe._diarization_import_error = None
    pipe._diarization_failed = False
    pipe._diarization_enabled = True

    monkeypatch.setattr(pipe, "_ensure_whisper", lambda: None)

    dummy_result = {
        "text": "hello world",
        "segments": [{"start": 0.0, "end": 1.0, "text": "hello world"}],
        "language": "en",
    }
    pipe._whisper_model = SimpleNamespace(
        transcribe=lambda *args, **kwargs: dummy_result
    )

    audio_path = base_config.temp_dir / "sample.mp3"
    audio_path.write_text("dummy")

    result = pipe.transcribe(audio_path)

    assert result["diarization"][0]["speaker"] == "SPEAKER_DI"
