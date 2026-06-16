# 006. Implement get_page tool

- **Priority:** P0
- **Type:** Tool

## Background

The workflow needs a reliable way to fetch page content and metadata.

## Goal

Add a page read tool that returns both markdown and HTML when available.

## Implementation Suggestion

- Map to `GET /api/pages/{id}`.
- Return a stable normalized payload.

## Acceptance Criteria

- The tool reads a page by ID.
- The output includes page metadata and content fields.

## Risk

BookStack may store HTML and markdown differently depending on the editor used last.
