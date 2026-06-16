# 022. Support tags mapping more completely

- **Priority:** P2
- **Type:** Data Mapping

## Background

Tags will matter more once pages are synced into other knowledge systems.

## Goal

Expand tag handling so it maps consistently from Dify inputs to BookStack outputs.

## Implementation Suggestion

- Preserve name/value pairs.
- Normalize output tag arrays.

## Acceptance Criteria

- Tag handling is documented and deterministic.

## Risk

Different BookStack instances may use tags in slightly different ways.
