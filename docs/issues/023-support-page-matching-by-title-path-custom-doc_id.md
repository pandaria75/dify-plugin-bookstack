# 023. Support page matching by title/path/custom doc_id

- **Priority:** P2
- **Type:** Tool Logic

## Background

Publishing by title alone may be too limited for real workflows.

## Goal

Expand `publish_page` matching strategies.

## Implementation Suggestion

- Support title matching.
- Support path matching.
- Leave room for custom document IDs later.

## Acceptance Criteria

- Matching strategy is configurable and documented.

## Risk

Too many match modes can make behavior harder to reason about.
