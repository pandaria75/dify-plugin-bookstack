# API Mapping

This document maps implemented Dify tools to BookStack API endpoints and distinguishes implemented tools from planned follow-up work.

## Phase 1 Tools

| Dify Tool | Status | BookStack API | Input | Output | Errors |
| --- | --- | --- | --- | --- | --- |
| `validate_credentials` | Implemented | `GET /api/system` | none | `success` boolean | invalid credentials, permission denied, invalid response, API unavailable |
| `search_pages` | Implemented | `GET /api/search` | `query` | page results | invalid credentials, permission denied, invalid response, API unavailable |
| `get_page` | Implemented | `GET /api/pages/{id}` | `page_id` | page content and metadata | invalid credentials, permission denied, page not found, invalid response, API unavailable |
| `create_page` | Implemented | `POST /api/pages` | title, markdown, book/chapter, tags | created page metadata | invalid credentials, permission denied, book not found, chapter not found, invalid response, API unavailable |
| `update_page` | Implemented | `PUT /api/pages/{id}` | page_id, title, markdown, tags | updated page metadata | invalid credentials, permission denied, page not found, invalid response, API unavailable |
| `publish_page` | Implemented | `GET + POST/PUT /api/pages` | page_id or match fields, content, location | create/update result | invalid match target, page not found |
| `list_books` | Implemented | `GET /api/books` | `count` and `offset` optional | books list with `count` and `total` | invalid credentials, permission denied, invalid response, API unavailable |
| `list_chapters` | Implemented | `GET /api/chapters` | `book_id`, `count`, and `offset` optional | chapters list with `count` and `total` | invalid credentials, permission denied, book not found, invalid response, API unavailable |

## Phase 2 Tools

| Dify Tool | Status | BookStack API | Input | Output | Errors |
| --- | --- | --- | --- | --- | --- |
| `list_shelves` | Implemented | `GET /api/shelves` | `count` and `offset` optional | shelves list with `count` and `total` | invalid credentials, permission denied, invalid response, API unavailable |
| `list_pages` | Implemented | `GET /api/pages` | `count` and `offset` optional | pages list with `count` and `total` | invalid credentials, permission denied, invalid response, API unavailable |

## Phase 2 Matching Enhancements

- `publish_page` matching order is `page_id`, then `doc_id` tag, then normalized `path`, then exact title fallback.
- Ambiguous `doc_id`, `path`, or title matches fail safely instead of updating an arbitrary page.
- Tag mapping is deterministic: inputs are normalized to `{name, value}` pairs; structured tag input is the unambiguous form when tag names or values contain delimiters.

## Notes

- The BookStack API uses `Authorization: Token <token_id>:<token_secret>`.
- The implemented tools already normalize response fields into Dify-friendly JSON output.
- `list_books`, `list_chapters`, `list_shelves`, and `list_pages` are implemented support tools before Datasource work begins.
- Shared error classification is centralized in `BookStackClient`: `401` -> `Invalid credentials`, `403` -> `Permission denied`, `404` -> method-specific not-found, `400/422` -> `Invalid BookStack response`, `429`/network timeout errors/`5xx` -> `BookStack API unavailable`, malformed or non-object JSON -> `Invalid BookStack response`, and other unexpected non-success responses -> `BookStack API unavailable`.
- Docker BookStack smoke validation on 2026-06-20 confirmed `system`, `books`, `chapters`, `shelves`, and `pages` API paths return HTTP 200 with configured local credentials; list endpoints returned `data` and `total` with an empty local dataset.
