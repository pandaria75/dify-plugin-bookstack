# 010. Add basic unit tests for BookStackClient and payload mapping

- **Priority:** P0
- **Type:** Testing

## Background

The client and tool payload mapping are the most likely places for regressions.

## Goal

Add focused tests for client behavior and request/response mapping.

## Implementation Suggestion

- Test credential parsing.
- Test base URL normalization.
- Test error translation.

## Acceptance Criteria

- Tests cover the client wrapper and key mapping helpers.
- Tests run without contacting real BookStack instances.

## Risk

Test fixtures may need adjustments once the real tool contracts are finalized.
