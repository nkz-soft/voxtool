---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED when the feature touches schema validation, parser
repair, metrics, pipeline orchestration, dataset generation, TTS, model running,
or report generation. The examples below include test tasks that MUST be adapted
for those areas when applicable.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit-tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management
- [ ] T010 [P] Define JSON output schema and validation fixtures
- [ ] T011 [P] Define dataset versioning and deterministic split configuration
- [ ] T012 Configure experiment artifact storage for inputs, raw outputs, parsed outputs, validation errors, and metrics
- [ ] T013 Configure CI jobs for lint, formatting check, typecheck, tests, and smoke benchmark
- [ ] T014 Configure GitHub Actions artifact upload with limited retention for benchmark outputs
- [ ] T015 Document manual or self-hosted GPU trigger for full audio/model benchmarks
- [ ] T016 Document public package, CLI, API, notebook, and benchmark-critical functions or methods

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (REQUIRED when touched by this story) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Schema validation test for [tool/output] in tests/unit/test_[name].py
- [ ] T018 [P] [US1] Parser repair test for invalid JSON handling in tests/unit/test_[name].py
- [ ] T019 [P] [US1] Metrics test for [benchmark metric] in tests/unit/test_[name].py
- [ ] T020 [P] [US1] Pipeline orchestration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T022 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T023 [US1] Implement [Service] in src/services/[service].py (depends on T021, T022)
- [ ] T024 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T025 [US1] Add schema validation and JSON failure handling
- [ ] T026 [US1] Add experiment artifact logging for user story 1 operations
- [ ] T027 [US1] Add descriptions for public functions, methods, and command/API surfaces

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (REQUIRED when touched by this story) ⚠️

- [ ] T028 [P] [US2] Schema validation test for [tool/output] in tests/unit/test_[name].py
- [ ] T029 [P] [US2] Parser repair or invalid JSON handling test in tests/unit/test_[name].py
- [ ] T030 [P] [US2] Metrics test for [benchmark metric] in tests/unit/test_[name].py
- [ ] T031 [P] [US2] Pipeline orchestration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T032 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T033 [US2] Implement [Service] in src/services/[service].py
- [ ] T034 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T035 [US2] Integrate with User Story 1 components (if needed)
- [ ] T036 [US2] Add descriptions for public functions, methods, and command/API surfaces

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (REQUIRED when touched by this story) ⚠️

- [ ] T037 [P] [US3] Schema validation test for [tool/output] in tests/unit/test_[name].py
- [ ] T038 [P] [US3] Metrics test for [benchmark metric] in tests/unit/test_[name].py
- [ ] T039 [P] [US3] Pipeline orchestration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T040 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T041 [US3] Implement [Service] in src/services/[service].py
- [ ] T042 [US3] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T043 [US3] Add descriptions for public functions, methods, and command/API surfaces

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Public function and method description review
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests required by changed benchmark components in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Verify large generated artifacts are excluded from Git
- [ ] TXXX Verify pull request evidence links to the spec task and validation results
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Required tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Schema validation test for [tool/output] in tests/unit/test_[name].py"
Task: "Pipeline orchestration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
