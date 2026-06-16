# 012. Implement list_books tool

- **Priority:** P1
- **Type:** Tool

## Background

Users need to select or inspect BookStack books.

## Goal

Add a tool that lists accessible books.

## Implementation Suggestion

- Map to `GET /api/books`.
- Allow basic pagination or filtering later.

## Acceptance Criteria

- The tool returns a books array with stable metadata fields.

## Risk

Large instances may require paging support sooner than expected.
