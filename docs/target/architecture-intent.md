# Target Architecture Intent

This file describes the intended future shape for the BookStack Dify plugin.

This is not evidence of how the project works today. Keep current-state facts in `docs/current/` and use this file for proposed direction, cleanup goals, migration intent, or future boundaries.

## Scope

- Area or workflow: BookStack Tool plugin first, Datasource plugin later.
- Why a target-state document is needed: keep planned capability separate from the current implemented Tool plugin scope.
- Status: approved direction for roadmap planning; implementation is incremental.
- Related current docs: `docs/current/system-map.md`, `docs/ARCHITECTURE.md`, `docs/API_MAPPING.md`, `docs/ROADMAP.md`.

## Desired Outcomes

- Provide a small, stable Tool plugin for BookStack read/write operations before expanding into Datasource behavior.
- Keep tool implementations thin, with BookStack HTTP behavior centralized in `BookStackClient`.
- Preserve safe credential handling and user-facing error terms as tools are added.
- Keep planned functionality visibly planned until implementation, validation, and docs are updated together.

## Proposed Future Shape

- Target:
  - Provider schema owns BookStack credentials and optional defaults.
  - `BookStackClient` owns base URL normalization, `/api` prefixing, auth header creation, timeout, SSL verification, request execution, JSON parsing, and error mapping.
  - Tool classes own Dify parameter handling, request mapping, and normalized response shaping.
  - Phase 1 grows from credential validation into page search/read/write and publish workflows.
  - Later Datasource work maps BookStack content into Dify Knowledge Pipeline records with stable metadata.
- Open design questions:
  - Exact normalized JSON response shape for each Phase 1 tool.
  - Packaging and smoke-test command for a real Dify plugin runtime.
  - Datasource sync scope and metadata model after Tool plugin behavior stabilizes.

## Differences From Current State

- Current fact:
  - The repository currently has the plugin skeleton, provider credential schema, provider validation, shared `BookStackClient`, `validate_credentials`, `search_pages`, `get_page`, `create_page`, `update_page`, and `publish_page`.
- Target:
  - The Tool plugin should support the planned Phase 1 BookStack operations, then later add Datasource behavior.
- Migration note:
  - Add one tool at a time, keeping YAML contracts, Python sources, tests, and planning docs synchronized.

## Assumptions And Tradeoffs

- Assumption:
  - BookStack's REST API remains the integration boundary for both Tool and future Datasource work.
  - Dify provider credentials remain the only place where BookStack secrets are configured.
- Tradeoff:
  - Centralizing HTTP behavior in `BookStackClient` reduces duplicated tool logic, but changes to that client can affect every tool.
  - Tool-first delivery gives earlier useful capability, but Datasource design remains deferred until Tool behavior is stable.

## Change Strategy

- Safe first steps: implement Phase 1 tools in roadmap order, starting with read-only behavior before side-effecting publish behavior.
- Required prerequisites: mock-based tests for `BookStackClient`, stable tool YAML contracts, and clear response/error mapping.
- Risks or rollback concerns: auth header leaks, incorrect BookStack endpoint mapping, side-effecting page writes, and Dify runtime packaging drift.
- Validation ideas: unit tests with mocked HTTP calls, targeted tool invocation checks, and a later package smoke test against a test Dify runtime.

## Non-Goals

- This target doc does not describe current availability of planned tools.
- This target doc does not define delete/archive behavior.
- This target doc does not replace `docs/API_MAPPING.md` for endpoint-level planning.
- Current runtime facts and unknowns remain in `docs/current/system-map.md` until implementation or verification changes them.

## Maintenance Notes

- Update this file when future direction changes.
- Do not rewrite current-state docs to match this target until the code or operational reality actually changes.
