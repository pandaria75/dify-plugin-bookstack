# 007. Implement create_page tool

- **Priority:** P0
- **Type:** Tool

## Background

Users need to create formal source pages from Dify outputs.

## Goal

Add a page creation tool with book, chapter, and tag support.

## Implementation Suggestion

- Map to `POST /api/pages`.
- Accept title, markdown, book/chapter target, and tags.

## Acceptance Criteria

- The tool creates a page in the selected location.
- The output includes `page_id`, `title`, and `url`.

## Risk

Location validation must avoid ambiguous behavior when both book and chapter are missing.
