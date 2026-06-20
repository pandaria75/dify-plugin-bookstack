# API Mapping

This document maps Phase 1 Dify tools to BookStack API endpoints and distinguishes implemented tools from planned follow-up work.

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

## Notes

- The BookStack API uses `Authorization: Token <token_id>:<token_secret>`.
- The implemented tools already normalize response fields into Dify-friendly JSON output.
- `list_books` and `list_chapters` are implemented Phase 1 support tools before Datasource work begins.
- Shared error classification is centralized in `BookStackClient`: `401` -> `Invalid credentials`, `403` -> `Permission denied`, `404` -> method-specific not-found, `400/422` -> `Invalid BookStack response`, `429`/network timeout errors/`5xx` -> `BookStack API unavailable`, malformed or non-object JSON -> `Invalid BookStack response`, and other unexpected non-success responses -> `BookStack API unavailable`.
