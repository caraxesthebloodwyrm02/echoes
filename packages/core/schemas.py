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

"""Data schemas for key components using Pydantic."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PodcastEvent(BaseModel):
    """Schema for podcast event data."""

    timestamp_start_s: float = Field(..., ge=0, description="Start time in seconds")
    timestamp_end_s: float = Field(..., ge=0, description="End time in seconds")
    speaker: Optional[str] = Field(None, description="Speaker name")
    utterance: str = Field(..., description="Spoken text")
    pause_after_s: float = Field(
        ..., ge=0, description="Pause duration after utterance"
    )
    label: str = Field(
        ..., description="Event label (cognitive_load, rhetorical, handoff, other)"
    )

    @field_validator("label")
    @classmethod
    def validate_label(cls, v):
        allowed = {"cognitive_load", "rhetorical", "handoff", "other"}
        if v not in allowed:
            raise ValueError(f"Label must be one of {allowed}")
        return v

    @field_validator("timestamp_end_s")
    @classmethod
    def validate_timestamps(cls, v, info):
        if (
            info.data
            and "timestamp_start_s" in info.data
            and v < info.data["timestamp_start_s"]
        ):
            raise ValueError("timestamp_end_s must be >= timestamp_start_s")
        return v


class PodcastData(BaseModel):
    """Schema for podcast episode data."""

    podcast: str = Field(..., description="Podcast name")
    episode_title: str = Field(..., description="Episode title")
    source: str = Field(..., description="Data source description")
    events: List[PodcastEvent] = Field(..., description="List of podcast events")


class PromptTemplate(BaseModel):
    """Schema for prompt templates."""

    id: str = Field(..., description="Unique template identifier")
    template: str = Field(..., description="Template text with placeholders")
    score: float = Field(..., ge=0, le=1, description="Template quality score")

    @field_validator("template")
    @classmethod
    def validate_template(cls, v):
        if not v.strip():
            raise ValueError("Template cannot be empty")
        return v


class CacheEntry(BaseModel):
    """Schema for prompt cache entries."""

    template_id: str = Field(..., description="Associated template ID")
    vec: List[float] = Field(..., description="Context vector representation")
    prompt: str = Field(..., description="Generated prompt text")
    score: float = Field(..., ge=0, le=1, description="Entry quality score")

    @field_validator("vec")
    @classmethod
    def validate_vector(cls, v):
        if len(v) == 0:
            raise ValueError("Vector cannot be empty")
        # Basic sanity check for vector length (adjust based on model)
        if len(v) > 4096:
            raise ValueError("Vector length exceeds maximum allowed (4096)")
        return v

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v


__all__ = ["PodcastEvent", "PodcastData", "PromptTemplate", "CacheEntry"]
