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

from __future__ import annotations

import logging
from pathlib import Path

import typer

from .config import Config
from .pipeline import MiniConPipeline

app = typer.Typer(help="MiniCon CLI: download → transcribe → write reports")

# Option definitions to avoid function calls in defaults
URL_ARG = typer.Argument(..., help="YouTube URL to process")
FILE_ARG = typer.Argument(..., help="Text file, one URL per line")
DRY_RUN_OPTION = typer.Option(
    False, "--dry-run", help="Print actions without writing files"
)
PRIMARY_DIR_OPTION = typer.Option(
    None, "--primary-dir", help="Primary report directory"
)
SECONDARY_DIR_OPTION = typer.Option(
    None, "--secondary-dir", help="Secondary mirror directory"
)
TEMP_DIR_OPTION = typer.Option(
    None, "--temp-dir", help="Temporary working directory for downloads"
)
MODEL_OPTION = typer.Option(
    None, "--model", help="Whisper model (tiny/base/small/medium/large)"
)
DIARIZATION_MODEL_OPTION = typer.Option(
    None, "--diarization-model", help="pyannote pipeline identifier to use"
)
DIARIZATION_MIN_OPTION = typer.Option(
    None, "--diarization-min", help="Minimum expected speakers"
)
DIARIZATION_MAX_OPTION = typer.Option(
    None, "--diarization-max", help="Maximum expected speakers"
)
DIARIZE_OPTION = typer.Option(
    False,
    "--diarize/--no-diarize",
    help="Enable speaker diarization (if supported by the model)",
)
FORCE_REDOWNLOAD_OPTION = typer.Option(
    False, "--force-redownload", help="Force re-download even if video is in cache"
)
FORCE_RETRANSCRIBE_OPTION = typer.Option(
    False,
    "--force-retranscribe",
    help="Force re-transcription even if transcription is in cache",
)


def _build_config(
    primary_report_dir: Path | None,
    secondary_report_dir: Path | None,
    temp_dir: Path | None,
    model: str | None,
    diarization_model: str | None,
    diarization_min_speakers: int | None,
    diarization_max_speakers: int | None,
) -> Config:
    cfg = Config.from_env()
    if primary_report_dir:
        cfg.report_dir_primary = primary_report_dir
    if secondary_report_dir is not None:
        cfg.report_dir_secondary = secondary_report_dir
    if temp_dir:
        cfg.temp_dir = temp_dir
    if model:
        cfg.model_name = model
    if diarization_model:
        cfg.diarization_model = diarization_model
    if diarization_min_speakers is not None:
        cfg.diarization_min_speakers = diarization_min_speakers
    if diarization_max_speakers is not None:
        cfg.diarization_max_speakers = diarization_max_speakers
    cfg.ensure_dirs()
    return cfg


def _make_logger(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")
    return logging.getLogger("minicon")


@app.command()
def transcribe(
    url: str = URL_ARG,
    dry_run: bool = DRY_RUN_OPTION,
    primary_report_dir: Path = PRIMARY_DIR_OPTION,
    secondary_report_dir: Path = SECONDARY_DIR_OPTION,
    temp_dir: Path = TEMP_DIR_OPTION,
    model: str = MODEL_OPTION,
    diarization_model: str = DIARIZATION_MODEL_OPTION,
    diarization_min_speakers: int = DIARIZATION_MIN_OPTION,
    diarization_max_speakers: int = DIARIZATION_MAX_OPTION,
    diarize: bool = DIARIZE_OPTION,
    force_redownload: bool = FORCE_REDOWNLOAD_OPTION,
    force_retranscribe: bool = FORCE_RETRANSCRIBE_OPTION,
):
    """Transcribe a single YouTube URL and write a report."""
    cfg = _build_config(
        primary_report_dir,
        secondary_report_dir,
        temp_dir,
        model,
        diarization_model,
        diarization_min_speakers,
        diarization_max_speakers,
    )
    log = _make_logger(cfg.log_level)
    pipe = MiniConPipeline(cfg, logger=log)

    # Enable diarization if requested
    if diarize:
        pipe.enable_diarization(True)

    # Process the URL with cache control options
    result = pipe.run_single(
        url,
        dry_run=dry_run,
        force_redownload=force_redownload,
        force_retranscribe=force_retranscribe,
    )

    if result and not dry_run:
        typer.echo(f"✅ Report saved: {result}")
    elif dry_run:
        typer.echo("✅ Dry run completed - no files were written")


@app.command("batch-transcribe")
def batch_transcribe(
    file_with_urls: Path = FILE_ARG,
    dry_run: bool = DRY_RUN_OPTION,
    primary_report_dir: Path = PRIMARY_DIR_OPTION,
    secondary_report_dir: Path = SECONDARY_DIR_OPTION,
    temp_dir: Path = TEMP_DIR_OPTION,
    model: str = MODEL_OPTION,
    diarization_model: str = DIARIZATION_MODEL_OPTION,
    diarization_min_speakers: int = DIARIZATION_MIN_OPTION,
    diarization_max_speakers: int = DIARIZATION_MAX_OPTION,
    diarize: bool = DIARIZE_OPTION,
    force_redownload: bool = FORCE_REDOWNLOAD_OPTION,
    force_retranscribe: bool = FORCE_RETRANSCRIBE_OPTION,
):
    """Process a file of URLs sequentially and write reports."""
    cfg = _build_config(
        primary_report_dir,
        secondary_report_dir,
        temp_dir,
        model,
        diarization_model,
        diarization_min_speakers,
        diarization_max_speakers,
    )
    log = _make_logger(cfg.log_level)
    pipe = MiniConPipeline(cfg, logger=log)

    # Enable diarization if requested
    if diarize:
        pipe.enable_diarization(True)

    # Process the batch with cache control options
    pipe.run_batch(
        file_with_urls,
        dry_run=dry_run,
        force_redownload=force_redownload,
        force_retranscribe=force_retranscribe,
    )

    if dry_run:
        typer.echo("✅ Batch dry run completed - no files were written")
    else:
        typer.echo("✅ Batch processing completed")


if __name__ == "__main__":
    app()
