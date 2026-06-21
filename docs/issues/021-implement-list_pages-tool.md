# 021. Implement list_pages tool

- **Priority:** P2
- **Type:** Tool
- **Status:** Implemented

## Background

Bulk page browsing will help later sync and auditing flows.

## Goal

Add a tool that lists pages.

## Implementation Suggestion

- Map to `GET /api/pages`.
- Use `count` and `offset` pagination.

## Acceptance Criteria

- Pages can be listed with stable metadata.

## Completion Notes

- Implemented as `list_pages` using `GET /api/pages`.
- Supports optional `count` and `offset` pagination parameters.
- Docker BookStack smoke validation confirmed the endpoint returns HTTP 200 and `data`/`total` list shape in the local environment.

## Risk

Result volume may require paging controls.
