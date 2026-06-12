from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Request
from packages.dataset_builder.models import Language
from packages.model_runner.prompts import PromptTemplateName, build_prompt
from packages.tts_synth.models import AudioExample, SynthesisSettings
from pydantic import BaseModel, ConfigDict, Field

from apps.api.demo import AudioDemoResponse, run_demo_prompt

router = APIRouter()


class AudioDemoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audio_path: str = Field(min_length=1)
    language: Language = "en"
    pipeline: Literal["C", "D"] = "C"
    execute_tool: bool = True


@router.post("/demo/audio")
def demo_audio(request: AudioDemoRequest, http_request: Request) -> AudioDemoResponse:
    """Run the Pipeline C or D audio tool-calling flow for one demo input."""
    state = http_request.app.state
    transcript = state.asr_adapter.transcribe(_demo_audio_example(request)).transcript

    if request.pipeline == "C":
        prompt = build_prompt(
            PromptTemplateName.PIPELINE_C_AUDIO_TOOL,
            registry=state.registry,
            input_text=transcript,
        )
    else:
        prompt = build_prompt(
            PromptTemplateName.PIPELINE_D_TRANSCRIPT_TOOL,
            registry=state.registry,
            transcript=transcript,
        )

    result = run_demo_prompt(
        prompt,
        text_adapter=state.text_adapter,
        registry=state.registry,
        executor=state.executor,
        execute_tool=request.execute_tool,
    )
    return AudioDemoResponse(transcript=transcript, **result.model_dump())


def _demo_audio_example(request: AudioDemoRequest) -> AudioExample:
    """Wrap an ad-hoc demo audio path in the AudioExample shape ASR adapters expect.

    The audio file stem is used as the audio_id, so MockASRAdapter transcript
    overrides can be keyed by stem in tests and local demos.
    """
    stem = Path(request.audio_path).stem or request.audio_path
    return AudioExample(
        audio_id=stem,
        example_id=stem,
        dataset_version="demo",
        language=request.language,
        split="test",
        reference_transcript=stem,
        audio_path=request.audio_path,
        tts_engine="demo",
        sample_rate_hz=16_000,
        synthesis_settings=SynthesisSettings(),
    )
