# 017. Add CI for lint and tests

- **Priority:** P1
- **Type:** CI

## Background

Automated checks will help keep the plugin stable as the implementation grows.

## Goal

Add GitHub Actions for tests and linting.

## Implementation Suggestion

- Run unit tests.
- Run a formatter or linter if adopted.
- Validate packaging later.

## Acceptance Criteria

- CI runs on pull requests.

## Risk

Tooling choices should remain light until the codebase grows.
