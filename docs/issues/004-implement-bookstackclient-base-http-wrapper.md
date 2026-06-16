# 004. Implement BookStackClient base HTTP wrapper

- **Priority:** P0
- **Type:** Core

## Background

All tools need a shared client that normalizes requests and errors.

## Goal

Implement a reusable HTTP wrapper for BookStack API calls.

## Implementation Suggestion

- Normalize the base URL.
- Prefix requests with `/api`.
- Add the Token authorization header.
- Map HTTP failures into readable exceptions.

## Acceptance Criteria

- Client supports credential validation and API request wrappers.
- Errors are translated into user-friendly domain errors.

## Risk

Response shape differences across BookStack versions may require extra mapping later.
