# 026. Add sync range by Book

- **Priority:** P2
- **Type:** Datasource

## Background

Book-level sync is a natural first sync scope.

## Goal

Allow Datasource sync to start from a specific book.

## Implementation Suggestion

- Traverse chapter and page hierarchy beneath the selected book.

## Acceptance Criteria

- Book-scoped sync is documented and testable.

## Risk

Large books may need pagination or batching.
