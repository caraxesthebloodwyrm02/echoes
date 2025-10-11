from __future__ import annotations

import logging
from pathlib import Path

import typer

from .config import Config
from .pipeline import MiniConPipeline

app = typer.Typer(help="MiniCon CLI: download → transcribe → write reports")


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
    url: str = typer.Argument(..., help="YouTube URL to process"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print actions without writing files"
    ),
    primary_report_dir: Path = typer.Option(
        None, "--primary-dir", help="Primary report directory"
    ),
    secondary_report_dir: Path = typer.Option(
        None, "--secondary-dir", help="Secondary mirror directory"
    ),
    temp_dir: Path = typer.Option(
        None, "--temp-dir", help="Temporary working directory for downloads"
    ),
    model: str = typer.Option(
        None, "--model", help="Whisper model (tiny/base/small/medium/large)"
    ),
    diarization_model: str = typer.Option(
        None, "--diarization-model", help="pyannote pipeline identifier to use"
    ),
    diarization_min_speakers: int = typer.Option(
        None, "--diarization-min", help="Minimum expected speakers"
    ),
    diarization_max_speakers: int = typer.Option(
        None, "--diarization-max", help="Maximum expected speakers"
    ),
    diarize: bool = typer.Option(
        False,
        "--diarize/--no-diarize",
        help="Enable speaker diarization (if supported by the model)",
    ),
    force_redownload: bool = typer.Option(
        False, "--force-redownload", help="Force re-download even if video is in cache"
    ),
    force_retranscribe: bool = typer.Option(
        False,
        "--force-retranscribe",
        help="Force re-transcription even if transcription is in cache",
    ),
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
    file_with_urls: Path = typer.Argument(..., help="Text file, one URL per line"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print actions without writing files"
    ),
    primary_report_dir: Path = typer.Option(
        None, "--primary-dir", help="Primary report directory"
    ),
    secondary_report_dir: Path = typer.Option(
        None, "--secondary-dir", help="Secondary mirror directory"
    ),
    temp_dir: Path = typer.Option(
        None, "--temp-dir", help="Temporary working directory for downloads"
    ),
    model: str = typer.Option(
        None, "--model", help="Whisper model (tiny/base/small/medium/large)"
    ),
    diarization_model: str = typer.Option(
        None, "--diarization-model", help="pyannote pipeline identifier to use"
    ),
    diarization_min_speakers: int = typer.Option(
        None, "--diarization-min", help="Minimum expected speakers"
    ),
    diarization_max_speakers: int = typer.Option(
        None, "--diarization-max", help="Maximum expected speakers"
    ),
    diarize: bool = typer.Option(
        False,
        "--diarize/--no-diarize",
        help="Enable speaker diarization (if supported by the model)",
    ),
    force_redownload: bool = typer.Option(
        False,
        "--force-redownload",
        help="Force re-download even if videos are in cache",
    ),
    force_retranscribe: bool = typer.Option(
        False,
        "--force-retranscribe",
        help="Force re-transcription even if transcriptions are in cache",
    ),
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
