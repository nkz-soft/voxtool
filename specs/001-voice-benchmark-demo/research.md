# Research: Multilingual Voice Benchmark Demo

## Decision: Python 3.11+ with uv

**Rationale**: Python has mature tooling for data generation, audio workflows,
model adapters, metrics, notebooks, FastAPI, and Typer. `uv` gives fast,
reproducible dependency management and command execution suitable for local
development and CI.

**Alternatives considered**:
- Poetry: mature but slower environment operations.
- Hatch: strong packaging support but less direct for the requested `uv` flow.
- Node.js: weaker fit for ASR/audio/data science workflows.

## Decision: Pydantic-owned tool schema package

**Rationale**: `packages/tool_schema` centralizes Pydantic models, JSON Schema
export, validation errors, and `units.convert` execution. This keeps the
schema-validation trust boundary explicit and reusable by CLI, API, pipelines,
and tests.

**Alternatives considered**:
- Hand-written JSON Schema only: avoids runtime model dependency but duplicates
  validation logic.
- Inline validation inside pipelines: faster to start but violates modularity
  and increases drift risk.

## Decision: Typer CLI plus optional FastAPI backend

**Rationale**: Typer supports reproducible command workflows for dataset
generation, audio synthesis, benchmark execution, and report building. FastAPI
is optional and limited to demo/backend execution of validated tool calls.

**Alternatives considered**:
- CLI only: simpler but less useful for a demo system.
- API first: over-emphasizes serving before benchmark reproducibility.

## Decision: MockModelAdapter for PR smoke benchmark

**Rationale**: MockModelAdapter makes PR benchmark output deterministic and
keeps CI independent of GPUs, paid APIs, real model downloads, and large audio
generation. About 30 examples are enough to cover all four pipelines, Russian
and English, tool-required and no-tool examples, invalid JSON, and invalid
schema cases.

**Alternatives considered**:
- Real small model in PR CI: higher realism but introduces download, runtime,
  and flakiness risks.
- Unit tests only: misses pipeline orchestration and artifact contracts.

## Decision: Manual-only full report workflow

**Rationale**: Full audio/model benchmarks, real model runs, paid API runs,
large audio generation, report generation, and release publishing are
manual-only. This preserves affordable PR CI while allowing controlled full
evaluation.

**Alternatives considered**:
- Scheduled full reports: useful for monitoring, but not requested and may
  create unexpected cost.
- Automatic full reports on main: too expensive and environment-dependent.

## Decision: Artifact retention split

**Rationale**: PR coverage and smoke benchmark artifacts are retained for 14
days, while manual full benchmark and release report artifacts are retained for
90 days. This supports review and comparison without retaining routine artifacts
indefinitely.

**Alternatives considered**:
- 7 days for all artifacts: too short for release/report review.
- 180 days for reports: useful historically but unnecessarily expensive for MVP.

## Decision: Generated artifacts excluded from Git

**Rationale**: Generated audio, evaluation results, reports, model files,
checkpoints, wandb, mlruns, and large datasets must stay out of Git. `.gitkeep`
and README files are allowed in artifact directories so expected paths exist and
usage is documented.

**Alternatives considered**:
- Commit generated smoke reports: easier browsing, but violates artifact policy.
- Git LFS: adds workflow overhead and is unnecessary for MVP generated outputs.

## Decision: Metrics grouped by tool-use, ASR, and modality gap

**Rationale**: The benchmark needs to compare tool-call correctness, transcript
quality, and differences between equivalent text/audio semantic examples. These
metric groups map directly to the four pipelines and the modality-gap goal.

**Alternatives considered**:
- Single aggregate score: simple but hides failure causes.
- Manual report-only scoring: not reproducible enough for benchmark-first work.
