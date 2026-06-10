from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from packages.dataset_builder.models import BenchmarkExample
from packages.model_runner.base import TextModelAdapter
from packages.model_runner.prompts import PromptTemplateName, build_prompt
from packages.pipeline_runner.artifacts import PipelineRunRecord, write_pipeline_jsonl
from packages.tool_schema.parser import parse_model_output
from packages.tool_schema.providers import ToolCall, ToolExecutor, ToolRegistry


def run_pipeline_a(
    examples: Iterable[BenchmarkExample],
    *,
    run_id: str,
    model_adapter: TextModelAdapter,
    registry: ToolRegistry,
    executor: ToolExecutor,
    output_path: Path | None = None,
) -> list[PipelineRunRecord]:
    """Run Pipeline A over text examples and optionally persist artifacts."""
    records = [
        _run_one_example(
            example,
            run_id=run_id,
            model_adapter=model_adapter,
            registry=registry,
            executor=executor,
        )
        for example in examples
    ]
    if output_path is not None:
        write_pipeline_jsonl(output_path, records)
    return records


def _run_one_example(
    example: BenchmarkExample,
    *,
    run_id: str,
    model_adapter: TextModelAdapter,
    registry: ToolRegistry,
    executor: ToolExecutor,
) -> PipelineRunRecord:
    prompt = build_prompt(
        PromptTemplateName.PIPELINE_A_TEXT_TOOL,
        registry=registry,
        input_text=example.text,
    )
    model_output = model_adapter.generate_text(prompt)
    parsed = parse_model_output(model_output.raw_output, registry=registry)
    tool_result = None
    structured_failures = list(parsed.structured_failures)

    if parsed.envelope is not None and parsed.envelope.tool_call is not None:
        tool_result = executor.execute(
            ToolCall(
                tool=parsed.envelope.tool_call.tool,
                arguments=parsed.envelope.tool_call.arguments.model_dump(mode="json"),
            )
        )
        if tool_result.failure is not None:
            structured_failures.append(tool_result.failure)

    final_answer = parsed.envelope.final_answer if parsed.envelope is not None else None
    return PipelineRunRecord(
        run_id=run_id,
        pipeline="A",
        example_id=example.example_id,
        dataset_version=example.dataset_version,
        model_adapter=model_output.adapter_name,
        input_modality="text",
        raw_output=parsed.raw_output,
        parsed_output=parsed.parsed_json,
        first_pass_parsable=parsed.first_pass_parsable,
        repair_attempted=parsed.repair_attempted,
        repair_success=parsed.repair_success,
        validation_errors=parsed.validation_errors,
        structured_failures=structured_failures,
        transcript=None,
        tool_execution_result=tool_result,
        final_answer=final_answer,
    )
