# 001. Initialize Dify plugin repository skeleton

- **Priority:** P0
- **Type:** Foundation

## Background

The project needs a stable repository shape that matches current Dify plugin expectations.

## Goal

Create the minimal plugin skeleton, root docs, and assets needed for a real implementation path.

## Implementation Suggestion

- Add `manifest.yaml`, `provider/`, `tools/`, `_assets/`, and `docs/`.
- Keep the initial code minimal and non-functional beyond structure.

## Acceptance Criteria

- Repository structure is clear.
- Dify plugin files are present.
- README and privacy documentation exist.

## Risk

Manifest schema drift may require small updates after a later packaging test.
