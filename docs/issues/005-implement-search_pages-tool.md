# 005. Implement search_pages tool

- **Priority:** P0
- **Type:** Tool

## Background

Users need a search entry point to locate pages by content or title.

## Goal

Add a BookStack page search tool for Dify workflows and agents.

## Implementation Suggestion

- Map the tool to BookStack search endpoints.
- Return page ID, title, and URL.

## Acceptance Criteria

- The tool accepts a query string.
- The tool returns a normalized results list.

## Risk

Search result ranking and filtering behavior may vary by BookStack instance.
