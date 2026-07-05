# Feature Specification: Piper Audio Dataset

**Feature Branch**: `004-piper-audio-dataset`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "I want to use Piper TTS to generate audio samples for testing models. This code should use Piper TTS and produce a dataset with audio samples created from text."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate test audio from demo text (Priority: P1)

A benchmark user can take the existing labeled bilingual demo dataset and generate an audio dataset from its text examples without manually uploading or recording audio.

**Why this priority**: This is the core value of the feature: model testing needs spoken samples that preserve the same labeled English and Russian task semantics as the text benchmark.

**Independent Test**: Can be fully tested by running the existing notebook helper flow with the demo dataset and confirming it produces usable audio records for every selected text example.

**Acceptance Scenarios**:

1. **Given** the labeled bilingual demo dataset is available, **When** the user calls `demo.synthesize_demo_audio(audio_dataset, output_dir="demo_audio")`, **Then** the output directory contains one generated audio sample per input example and metadata that links each sample to the original example.
2. **Given** the input dataset contains both English and Russian examples, **When** audio generation completes, **Then** the resulting audio dataset preserves the original language labels, example identifiers, dataset version, and split membership.
3. **Given** a generated audio dataset exists, **When** it is passed into the audio model testing flow, **Then** the flow can use each audio sample together with its reference transcript and benchmark labels.

---

### User Story 2 - Preserve reproducible benchmark artifacts (Priority: P2)

A benchmark maintainer can regenerate the audio samples later and compare runs because the output records clearly describe how each sample was created.

**Why this priority**: Audio generation changes benchmark inputs, so repeatability and traceability are required before model comparison results are meaningful.

**Independent Test**: Can be tested by generating the same bounded dataset twice and verifying that both runs produce the same record set, semantic links, synthesis settings, and usable audio files.

**Acceptance Scenarios**:

1. **Given** the same input dataset and synthesis configuration, **When** audio generation is repeated, **Then** the produced metadata references the same source examples and synthesis settings.
2. **Given** audio generation finishes, **When** a user inspects the metadata, **Then** each record includes the audio path, reference transcript, language, split, source example identifier, duration or equivalent timing information, and selected voice information when available.

---

### User Story 3 - Handle unavailable synthesis resources clearly (Priority: P3)

A user receives an actionable failure when the selected synthesis engine or voice resources are unavailable, rather than getting incomplete or silently invalid benchmark data.

**Why this priority**: Piper-based generation depends on local synthesis resources that may be missing in a fresh environment, and silent fallback would make benchmark evidence misleading.

**Independent Test**: Can be tested by running audio generation without the required synthesis resources and confirming that no partial dataset is reported as successful.

**Acceptance Scenarios**:

1. **Given** required synthesis resources are missing, **When** the user requests audio generation, **Then** the system stops with a clear message explaining what resource is unavailable and no successful dataset manifest is produced.
2. **Given** one example fails synthesis, **When** generation cannot complete the full requested dataset, **Then** the failure is reported with the affected example and the run is not presented as a complete benchmark dataset.

### Edge Cases

- The input dataset is empty.
- Two examples resolve to the same desired audio identifier or path.
- Output files already exist from a previous run.
- A source text is unusually long, blank, or contains punctuation and units used by the benchmark tasks.
- English and Russian examples require different voices or language-specific synthesis resources.
- Audio generation is interrupted after only part of the dataset is written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate audio samples from existing labeled text benchmark examples using Piper TTS as the selected synthesis engine.
- **FR-002**: Users MUST be able to generate audio through the existing demo helper flow shown in the notebook example without changing the high-level call pattern.
- **FR-003**: System MUST produce one audio dataset record for each successfully synthesized input example.
- **FR-004**: Each audio dataset record MUST remain traceable to the original text example, including source example identifier, dataset version, language, split, and reference transcript.
- **FR-005**: System MUST preserve semantic alignment between text and audio examples so text and audio model results can be compared for the same benchmark task.
- **FR-006**: System MUST record enough synthesis details for each generated sample to identify the synthesis engine, selected voice when known, sample rate, duration or equivalent timing, and output audio path.
- **FR-007**: System MUST avoid silently falling back to placeholder or silent audio when Piper synthesis is requested.
- **FR-008**: System MUST report missing or unusable synthesis resources as a clear generation failure.
- **FR-009**: System MUST prevent a partial synthesis run from being reported as a complete audio dataset.
- **FR-010**: System MUST support both Russian and English examples from the labeled bilingual dataset.
- **FR-011**: System MUST keep generated audio artifacts outside committed source files while allowing small fixtures or metadata needed for tests.
- **FR-012**: System MUST define benchmark validation evidence before declaring the feature successful.
- **FR-013**: System MUST keep ordinary CI bounded by using small fixtures, mocks, or resource-availability checks rather than requiring large downloads or full audio generation.
- **FR-014**: System MUST support manual validation that generates real Piper audio samples for a bounded bilingual dataset.
- **FR-015**: Public notebook helpers, command surfaces, and package interfaces introduced or changed by this feature MUST have concise descriptions.

### Key Entities *(include if feature involves data)*

- **Text Benchmark Example**: A labeled English or Russian benchmark request with stable identifiers, split membership, expected tool behavior, and source text.
- **Audio Dataset Record**: A generated audio sample plus metadata that links it to one text benchmark example and describes synthesis settings.
- **Synthesis Configuration**: The selected synthesis engine, voice selection, language handling, and audio output settings used to create samples.
- **Generation Run**: A bounded audio dataset creation attempt with completion status, produced records, and failure details when generation cannot finish.

### Benchmark and Dataset Requirements *(mandatory for benchmark changes)*

- **Dataset Version**: The audio dataset MUST reference the source text dataset version and MUST expose its own generation metadata so audio benchmark runs can identify which synthesis configuration created the samples.
- **Split Strategy**: Audio examples MUST inherit deterministic train, validation, and test split membership from their source text examples.
- **Languages**: Russian and English MUST be supported because the source demo dataset is bilingual and modality comparisons require both languages.
- **Modalities**: Text and audio MUST stay aligned by source example identifier so the same semantic request can be evaluated in both modalities.
- **Allowed Tools**: The feature MUST preserve the tool labels already present in the source benchmark examples and MUST NOT introduce weather as a required benchmark behavior.
- **Artifact Logging**: Generated dataset metadata MUST include source identifiers, reference transcripts, audio paths, synthesis settings, and generation status sufficient for later model-test evidence.
- **Failure Handling**: Missing synthesis resources, invalid input records, path collisions, and incomplete generation MUST be reported as failures instead of producing misleading complete manifests.
- **CI Evidence**: Validation MUST include lint, formatting check, typecheck, tests, and a bounded smoke path that does not require full real-audio generation in ordinary CI.
- **Full Benchmark Trigger**: Real Piper audio generation and downstream model testing MAY be run manually or in a suitable workflow and MUST save artifact paths for review.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can generate audio records for 100% of a bounded bilingual demo dataset with a single helper call using the existing notebook flow.
- **SC-002**: 100% of generated audio records include source example identifier, language, split, reference transcript, audio path, synthesis settings, and selected voice information when available.
- **SC-003**: 100% of generated audio records preserve the source dataset version and split membership from the text examples.
- **SC-004**: A missing synthesis resource results in a clear failure before a complete dataset manifest is reported.
- **SC-005**: Ordinary CI validates the feature without downloading large synthesis assets or committing generated audio artifacts.
- **SC-006**: Manual validation produces real audio samples for at least one English example and one Russian example and records the artifact locations for model testing.

## Assumptions

- Piper TTS is the required real-audio synthesis engine for this feature.
- The current silent fixture path remains available for bounded tests and CI where real synthesis resources are intentionally unavailable.
- The initial user-facing flow is the existing notebook helper call shown in the request.
- Generated audio files are local artifacts and are not committed to Git.
- If language-specific voices are needed, the generation configuration can select appropriate English and Russian voices while preserving one output record per source example.
