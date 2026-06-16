# 014. Improve error handling and user-facing error messages

- **Priority:** P1
- **Type:** Reliability

## Background

Tool users need actionable errors, not raw HTTP traces.

## Goal

Improve error translation and make all tool errors consistent.

## Implementation Suggestion

- Centralize BookStack error mapping.
- Keep the final error text short.

## Acceptance Criteria

- Common failure modes map to the documented error strings.

## Risk

Some BookStack responses may not contain enough detail for perfect mapping.
