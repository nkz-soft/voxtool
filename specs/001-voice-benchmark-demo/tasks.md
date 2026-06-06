# Tasks: Initial Project Structure and GitHub CI/CD

**Input**: Design documents from `/specs/001-voice-benchmark-demo/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Scope**: Initial repository scaffold, Python monorepo metadata, configuration
files, GitHub workflows, GitHub issue/PR templates, README/developer commands,
and validation tasks. Benchmark implementation internals are intentionally left
for later task batches.

A later task batch MUST cover `units.convert`, schema validation, parser repair,
dataset generation, TTS synthesis, model adapters, pipelines A-D, metrics, and
report generation before full feature implementation is considered complete.

**Format**: `[ID] [P?] Description with exact file path`

## Phase 1: Speckit and Repository Metadata

**Purpose**: Preserve feature planning artifacts and define repository artifact policy before code scaffold work begins.

- [ ] T001 Create feature task index in specs/001-voice-benchmark-demo/tasks.md
- [ ] T002 [P] Add generated artifact exclusions to .gitignore
- [ ] T003 [P] Add repository editor settings for Python formatting in .editorconfig
- [ ] T004 [P] Add artifact directory policy notes in data/README.md
- [ ] T005 [P] Add report artifact policy notes in reports/README.md
- [ ] T006 [P] Add placeholder file for raw data directory in data/raw/.gitkeep
- [ ] T007 [P] Add placeholder file for processed data directory in data/processed/.gitkeep
- [ ] T008 [P] Add placeholder file for reports directory in reports/.gitkeep

## Phase 2: Python Monorepo Scaffold

**Purpose**: Establish the Python 3.11+ uv monorepo layout and importable package boundaries.

- [ ] T009 Create Python project metadata with uv dependency groups in pyproject.toml
- [ ] T010 Create uv lockfile for the initial dependency set in uv.lock
- [ ] T011 Create developer command targets in Makefile
- [ ] T012 [P] Create optional FastAPI app package marker in apps/api/__init__.py
- [ ] T013 [P] Create optional FastAPI app entrypoint stub in apps/api/main.py
- [ ] T014 [P] Create Typer CLI package marker in apps/cli/__init__.py
- [ ] T015 [P] Create Typer CLI entrypoint stub in apps/cli/__main__.py
- [ ] T016 [P] Create notebook directory README in apps/notebook/README.md
- [ ] T017 [P] Create tool schema package marker in packages/tool_schema/__init__.py
- [ ] T018 [P] Create dataset builder package marker in packages/dataset_builder/__init__.py
- [ ] T019 [P] Create TTS synthesis package marker in packages/tts_synth/__init__.py
- [ ] T020 [P] Create model runner package marker in packages/model_runner/__init__.py
- [ ] T021 [P] Create pipeline runner package marker in packages/pipeline_runner/__init__.py
- [ ] T022 [P] Create metrics package marker in packages/metrics/__init__.py
- [ ] T023 [P] Create report builder package marker in packages/report_builder/__init__.py
- [ ] T024 [P] Create dataset generation script stub in scripts/generate_dataset.py
- [ ] T025 [P] Create audio synthesis script stub in scripts/synthesize_audio.py
- [ ] T026 [P] Create benchmark execution script stub in scripts/run_benchmark.py
- [ ] T027 [P] Create report building script stub in scripts/build_report.py
- [ ] T028 [P] Create unit test package placeholder in tests/unit/__init__.py
- [ ] T029 [P] Create integration test package placeholder in tests/integration/__init__.py
- [ ] T030 [P] Create e2e test package placeholder in tests/e2e/__init__.py

## Phase 3: Configuration Files

**Purpose**: Add baseline tool, prompt, model, experiment, lint, typecheck, and test configuration files.

- [ ] T031 [P] Add units.convert tool configuration in configs/tools/units.convert.yml
- [ ] T032 [P] Add MVP prompt configuration in configs/prompts/mvp.yml
- [ ] T033 [P] Add mock model configuration in configs/models/mock.yml
- [ ] T034 [P] Add smoke benchmark experiment configuration in configs/experiments/smoke.yml
- [ ] T035 [P] Add full report experiment configuration template in configs/experiments/full-report.yml
- [ ] T036 Add ruff lint and format configuration in pyproject.toml
- [ ] T037 Add mypy strictness and package path configuration in pyproject.toml
- [ ] T038 Add pytest and coverage configuration in pyproject.toml
- [ ] T039 [P] Add Python version pin in .python-version

## Phase 4: GitHub Workflows

**Purpose**: Configure required GitHub Actions workflows without GPU, paid API, real model download, or large audio requirements in PR CI.

- [ ] T040 Create CI workflow for push and pull_request to main/develop in .github/workflows/ci.yml
- [ ] T041 Add ruff check, ruff format --check, mypy, pytest, and coverage.xml upload jobs in .github/workflows/ci.yml
- [ ] T042 Configure coverage.xml artifact upload with 14-day retention in .github/workflows/ci.yml
- [ ] T043 Create deterministic smoke benchmark workflow in .github/workflows/benchmark-smoke.yml
- [ ] T044 Configure benchmark-smoke.yml pull_request and workflow_dispatch triggers in .github/workflows/benchmark-smoke.yml
- [ ] T045 Configure MockModelAdapter smoke command and 30-example limit in .github/workflows/benchmark-smoke.yml
- [ ] T046 Configure smoke benchmark artifact upload with 14-day retention in .github/workflows/benchmark-smoke.yml
- [ ] T047 Create manual report workflow in .github/workflows/report.yml
- [ ] T048 Configure report.yml workflow_dispatch model and limit inputs in .github/workflows/report.yml
- [ ] T049 Configure report artifact upload with 90-day retention in .github/workflows/report.yml
- [ ] T050 Create tag-based release workflow in .github/workflows/release.yml
- [ ] T051 Configure v*.*.* tag trigger and smoke report artifact attachment in .github/workflows/release.yml
- [ ] T052 Configure release report artifact retention for 90 days in .github/workflows/release.yml
- [ ] T053 Create weekly Dependabot updates for GitHub Actions and Python dependencies in .github/dependabot.yml

## Phase 5: GitHub Issue and PR Templates

**Purpose**: Add repository collaboration templates required for Speckit traceability and experiment tracking.

- [ ] T054 [P] Create Feature Task issue form in .github/ISSUE_TEMPLATE/feature_task.yml
- [ ] T055 [P] Create Benchmark Experiment issue form with hypothesis, pipeline, setup, metrics, and result fields in .github/ISSUE_TEMPLATE/benchmark_experiment.yml
- [ ] T056 [P] Create Bug issue form in .github/ISSUE_TEMPLATE/bug.yml
- [ ] T057 [P] Create Documentation/Process issue form in .github/ISSUE_TEMPLATE/documentation_process.yml
- [ ] T058 Create pull request template requiring Speckit task IDs in .github/pull_request_template.md
- [ ] T059 Add PR validation checklist for CI, benchmark-smoke, artifacts, and validation evidence in .github/pull_request_template.md

## Phase 6: README and Developer Commands

**Purpose**: Document setup, commands, CI status, artifact policy, and contributor expectations.

- [ ] T060 Add project overview and CI badges in README.md
- [ ] T061 Add fresh clone setup commands for make install, make lint, make typecheck, and make test in README.md
- [ ] T062 Add benchmark-smoke workflow explanation and PR expectations in README.md
- [ ] T063 Add artifact policy for generated audio, eval results, reports, model files, checkpoints, wandb, mlruns, and large datasets in README.md
- [ ] T064 Add release workflow and report artifact notes in README.md
- [ ] T065 Add Makefile target for make install in Makefile
- [ ] T066 Add Makefile target for make lint in Makefile
- [ ] T067 Add Makefile target for make typecheck in Makefile
- [ ] T068 Add Makefile target for make test in Makefile
- [ ] T069 Add Makefile target for make benchmark-smoke in Makefile

## Phase 7: Validation

**Purpose**: Verify the scaffold and CI/CD configuration meet the acceptance criteria.

- [ ] T070 Validate pyproject syntax and uv environment setup using pyproject.toml
- [ ] T071 Validate GitHub workflow YAML syntax for .github/workflows/ci.yml
- [ ] T072 Validate GitHub workflow YAML syntax for .github/workflows/benchmark-smoke.yml
- [ ] T073 Validate GitHub workflow YAML syntax for .github/workflows/report.yml
- [ ] T074 Validate GitHub workflow YAML syntax for .github/workflows/release.yml
- [ ] T075 Run make lint and record result in specs/001-voice-benchmark-demo/validation.md
- [ ] T076 Run make typecheck and record result in specs/001-voice-benchmark-demo/validation.md
- [ ] T077 Run make test and record result in specs/001-voice-benchmark-demo/validation.md
- [ ] T078 Run make benchmark-smoke and record artifact paths in specs/001-voice-benchmark-demo/validation.md
- [ ] T079 Verify generated artifact exclusions cover audio, eval results, reports, model files, checkpoints, wandb, mlruns, and large datasets in .gitignore
- [ ] T080 Verify README badges, PR template checklist, issue forms, and Dependabot config in specs/001-voice-benchmark-demo/validation.md

## Dependencies & Execution Order

- **Phase 1** must complete first because it defines repository metadata and artifact policy.
- **Phase 2** depends on Phase 1 and creates the filesystem structure used by later configuration and workflows.
- **Phase 3** depends on Phase 2 for package and config paths.
- **Phase 4** depends on Phases 2 and 3 because workflow commands reference project commands and configs.
- **Phase 5** can run after Phase 1 and is independent of Phase 4.
- **Phase 6** depends on Phases 2-5 so README and Makefile commands match real files.
- **Phase 7** depends on all previous phases.

## Parallel Opportunities

- T004-T008 can run in parallel after T002.
- T012-T030 can run in parallel after T009-T011 define project metadata and commands.
- T031-T035 and T039 can run in parallel before pyproject updates T036-T038.
- T043-T053 can run in parallel with T054-T057 after directory creation.
- T060-T064 can run in parallel with T065-T069 if README and Makefile are edited by separate workers.
- T071-T074 can run in parallel after workflow files exist.

## Independent Validation Criteria

- **Speckit and repository metadata**: Artifact policy files and placeholders exist at exact paths, and .gitignore covers generated outputs.
- **Python monorepo scaffold**: All app, package, script, and test placeholder paths exist and import/package names are stable.
- **Configuration files**: Tool, prompt, model, and experiment config files exist and pyproject defines lint, typecheck, test, and coverage behavior.
- **GitHub workflows**: CI and smoke workflows run on PR without GPU/paid API/model download/large audio requirements; manual workflows use workflow_dispatch or tag triggers as specified.
- **GitHub templates**: PR template requires Speckit task IDs and validation evidence; issue forms cover all required issue types.
- **README and commands**: Fresh clone commands are documented and Makefile exposes install, lint, typecheck, test, and benchmark-smoke.
- **Validation**: Validation results are recorded in specs/001-voice-benchmark-demo/validation.md.

## Suggested MVP Scope

Complete Phases 1-7 for scaffold and CI/CD only. Do not implement full benchmark
logic beyond stubs required for commands and workflow wiring in this task batch.
