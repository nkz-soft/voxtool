<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- I. Benchmark-First Evaluation: unchanged
- II. Validated Tool Invocation: unchanged
- III. Machine-Readable Model Output: unchanged
- IV. Versioned Multilingual Datasets: unchanged
- V. Experiment Traceability and Modular Design: expanded with CI and artifact rules
Added sections:
- CI, Artifacts, and Pull Requests
Removed sections:
- None
Templates requiring updates:
- .specify/templates/plan-template.md: updated
- .specify/templates/spec-template.md: updated
- .specify/templates/tasks-template.md: updated
- .specify/templates/commands/*.md: not present
Follow-up TODOs: none
-->
# Voice Assistant ToolBench Constitution

## Core Principles

### I. Benchmark-First Evaluation
Every pipeline MUST be evaluated with reproducible metrics before it is called
successful. A feature that changes dataset generation, TTS, model execution,
pipeline orchestration, metrics, or reports MUST define success criteria before
implementation and MUST record metric outputs in a repeatable form. Claims based
only on manual inspection are not accepted because this project exists to compare
voice assistant tool-use behavior reliably.

### II. Validated Tool Invocation
Tool calls MUST NOT be executed until the requested tool name, arguments, and
argument types pass schema validation. Validation failures MUST be treated as
pipeline failures, logged, and included in experiment artifacts. This protects
benchmarks from silently rewarding malformed or unsafe tool-use behavior.

### III. Machine-Readable Model Output
Model output MUST be machine-readable JSON. Invalid JSON is a failure and MUST
be logged with the raw output, repair attempt if any, parsed result if any, and
validation error. Parser repair MAY be used for analysis, but repaired output
MUST remain distinguishable from valid first-pass JSON in metrics and reports.

### IV. Versioned Multilingual Datasets
All datasets MUST be versioned and MUST use deterministic train, validation, and
test splits. Russian and English requests MUST be supported. Text and audio
evaluations MUST use the same semantic examples so reports can measure the
modality gap between written and spoken requests without confounding the task
content.

### V. Experiment Traceability and Modular Design
Every experiment MUST save inputs, raw model outputs, parsed outputs, validation
errors, and metrics. Implementation MUST keep dataset generation, TTS, model
runner, pipeline runner, metrics, and report generation in separate packages or
modules with clear interfaces. Tests are REQUIRED for schema validation, parser
repair, metrics, and pipeline orchestration because these components define the
trust boundary of the benchmark. Large generated artifacts MUST NOT be committed
to Git; reproducible generation steps and bounded metadata belong in the
repository instead.

## Tool and Modality Constraints

The primary MVP benchmark tool is `units.convert`. Weather is not part of the
MVP and MUST NOT be required by MVP datasets, prompts, schemas, pipelines, tests,
or reports. Any feature introducing tools, schemas, examples, prompts, or reports
MUST keep the supported tool set explicit and MUST reject examples that require
unsupported tools.

Audio and text paths MUST share semantic examples. TTS generation, audio model
inputs, and text model inputs MAY differ in representation, but they MUST remain
traceable to the same dataset item and split. Reports MUST expose text metrics,
audio metrics, and modality-gap comparisons for the same task semantics.

## Development Workflow and Quality Gates

Feature specifications MUST define benchmark metrics, dataset versioning and
split behavior, JSON output handling, schema-validation behavior, artifact
logging, and Russian/English coverage when applicable. Implementation plans MUST
identify the affected package boundary: dataset generation, TTS, model runner,
pipeline runner, metrics, report generation, or tests.

Task plans MUST include tests for schema validation, parser repair, metrics, and
pipeline orchestration whenever those components are changed. A feature is not
complete until tests pass and a reproducible benchmark or validation command
produces the required saved artifacts.

## CI, Artifacts, and Pull Requests

CI is mandatory. Every pull request MUST run lint, formatting check, typecheck,
tests, and a smoke benchmark. Full audio/model benchmarks MUST be manually
triggered or run on self-hosted GPU runners, and they MUST NOT block ordinary CI
unless the feature explicitly changes full-benchmark behavior.

Benchmark outputs produced by CI MUST be uploaded as GitHub Actions artifacts
with limited retention. Large generated artifacts, including datasets, audio,
model outputs, benchmark reports, and raw experiment directories, MUST NOT be
committed to Git unless a documented exception is approved in the plan.

Every pull request MUST link to a spec task and include validation evidence:
the CI run, smoke benchmark result, relevant manual benchmark artifact when
applicable, and any known deviations from this constitution.

## Governance

This constitution supersedes conflicting project practices, templates, and
implementation shortcuts. Amendments require a documented change to this file,
an updated Sync Impact Report, and updates to affected Spec Kit templates or
runtime guidance. Versioning follows semantic versioning: MAJOR for incompatible
principle removals or redefinitions, MINOR for new principles or materially
expanded governance, and PATCH for clarifications that preserve existing rules.

Compliance review is required during specification, planning, task generation,
implementation review, and pull request review. Any planned violation MUST be
listed in the plan's Complexity Tracking table with a concrete rationale and a
rejected simpler alternative. Unresolved violations block implementation
completion and pull request merge.

**Version**: 1.1.0 | **Ratified**: 2026-06-05 | **Last Amended**: 2026-06-05
