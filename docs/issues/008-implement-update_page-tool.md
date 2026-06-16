# 008. Implement update_page tool

- **Priority:** P0
- **Type:** Tool

## Background

Users need to revise an existing page without recreating it.

## Goal

Add a page update tool keyed by page ID.

## Implementation Suggestion

- Map to `PUT /api/pages/{id}`.
- Allow title, markdown, tags, and optional parent movement.

## Acceptance Criteria

- Existing page content can be updated.
- The output includes the updated page metadata.

## Risk

Moving a page between book and chapter parents may need extra validation.
