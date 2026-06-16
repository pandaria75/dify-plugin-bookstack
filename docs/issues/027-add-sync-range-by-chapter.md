# 027. Add sync range by Chapter

- **Priority:** P2
- **Type:** Datasource

## Background

Chapter-scoped sync will allow more precise content ingestion.

## Goal

Allow Datasource sync to start from a specific chapter.

## Implementation Suggestion

- Traverse pages under the selected chapter.

## Acceptance Criteria

- Chapter-scoped sync is supported.

## Risk

Parent-child page structure may require extra normalization.
