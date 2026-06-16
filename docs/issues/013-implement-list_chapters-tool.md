# 013. Implement list_chapters tool

- **Priority:** P1
- **Type:** Tool

## Background

Publishing often requires selecting the correct chapter within a book.

## Goal

Add a chapter listing tool.

## Implementation Suggestion

- Map to `GET /api/chapters`.
- Support filtering by `book_id`.

## Acceptance Criteria

- Chapters can be listed by book.
- The output is normalized for Dify workflows.

## Risk

Instances with deeply nested content may need more context fields later.
