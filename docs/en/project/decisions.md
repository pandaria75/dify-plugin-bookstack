# Project Decisions

## Current Document Purpose

This file captures durable project decisions behind the current documentation and plugin shape.

## Decisions

### 1. Tool-first repository direction

The repository started as a BookStack Tool plugin first because the immediate use case was workflow automation for BookStack page operations.

### 2. Datasource follows as a separate package

Datasource support exists as a separate `bookstack_datasource/` package instead of being merged into the root Tool plugin package.

### 3. Shared BookStack behavior belongs in `BookStackClient`

Base URL normalization, `/api` prefixing, auth header construction, timeout and SSL behavior, and user-facing error mapping belong in the shared client layer.

### 4. User-facing error terms stay stable

The repository uses stable error terms such as `Invalid credentials`, `Permission denied`, `Book not found`, `Chapter not found`, `Page not found`, `BookStack API unavailable`, and `Invalid BookStack response`.

### 5. Repository-relative plugin paths are the local convention

Plugin YAML references and `extra.python.source` values use repository-relative paths.

### 6. Datasource client reuse currently uses deterministic generation

Root `bookstack_client.py` stays canonical, while the Datasource package uses a generated subset plus sync/check validation to avoid manual drift.

### 7. Release-readiness stays conservative

Marketplace and release work should not overstate current capability. The project keeps implemented features documented as implemented and planned follow-up work documented as planned.
