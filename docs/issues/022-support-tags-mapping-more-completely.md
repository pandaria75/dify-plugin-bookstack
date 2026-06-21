# 022. Support tags mapping more completely

- **Priority:** P2
- **Type:** Data Mapping
- **Status:** Implemented

## Background

Tags will matter more once pages are synced into other knowledge systems.

## Goal

Expand tag handling so it maps consistently from Dify inputs to BookStack outputs.

## Implementation Suggestion

- Preserve name/value pairs.
- Normalize output tag arrays.

## Acceptance Criteria

- Tag handling is documented and deterministic.

## Completion Notes

- Tag inputs normalize to BookStack-style objects with `name` and `value` fields.
- `name:value` strings are supported for compatibility; structured tag objects are preferred when delimiter ambiguity matters.
- Empty tag names are ignored and tag order is preserved.

## Risk

Different BookStack instances may use tags in slightly different ways.
