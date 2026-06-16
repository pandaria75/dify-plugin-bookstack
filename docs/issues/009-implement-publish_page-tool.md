# 009. Implement publish_page tool

- **Priority:** P0
- **Type:** Tool

## Background

This is the core business flow for the project.

## Goal

Implement create-or-update publishing logic with page matching support.

## Implementation Suggestion

- Support explicit `page_id` updates.
- Support matching by title or path.
- Create a page when no existing target is found.

## Acceptance Criteria

- The tool returns `action`, `page_id`, `title`, `url`, and `success`.
- Update and create flows both work through one entry point.

## Risk

Page matching strategies can become ambiguous if titles are duplicated.
