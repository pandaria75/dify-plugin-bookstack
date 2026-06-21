# 023. Support page matching by title/path/custom doc_id

- **Priority:** P2
- **Type:** Tool Logic
- **Status:** Implemented

## Background

Publishing by title alone may be too limited for real workflows.

## Goal

Expand `publish_page` matching strategies.

## Implementation Suggestion

- Support exact title matching.
- Support normalized path matching.
- Support custom document IDs through a `doc_id` page tag.

## Acceptance Criteria

- Matching strategy is configurable and documented.

## Completion Notes

- `publish_page` matching order is `page_id`, then `doc_id`, then `path`, then exact title fallback.
- Ambiguous matches fail safely instead of updating an arbitrary page.
- When `doc_id` is provided, `publish_page` adds a `doc_id` tag unless one is already present.

## Risk

Too many match modes can make behavior harder to reason about.
