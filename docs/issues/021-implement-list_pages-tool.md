# 021. Implement list_pages tool

- **Priority:** P2
- **Type:** Tool

## Background

Bulk page browsing will help later sync and auditing flows.

## Goal

Add a tool that lists pages.

## Implementation Suggestion

- Map to `GET /api/pages`.
- Support book and chapter filters later.

## Acceptance Criteria

- Pages can be listed with stable metadata.

## Risk

Result volume may require paging controls.
