# 020. Implement list_shelves tool

- **Priority:** P2
- **Type:** Tool
- **Status:** Implemented

## Background

Shelf-level organization is useful but not required for the MVP.

## Goal

Add a tool that lists shelves.

## Implementation Suggestion

- Map to `GET /api/shelves`.

## Acceptance Criteria

- Shelves can be listed with normalized output.

## Completion Notes

- Implemented as `list_shelves` using `GET /api/shelves`.
- Supports optional `count` and `offset` pagination parameters.
- Docker BookStack smoke validation confirmed the endpoint returns HTTP 200 and `data`/`total` list shape in the local environment.

## Risk

Shelf data may require additional pagination support.
