# API Mapping

This document maps Phase 1 Dify tools to BookStack API endpoints and distinguishes implemented tools from planned follow-up work.

## Phase 1 Tools

| Dify Tool | Status | BookStack API | Input | Output | Errors |
| --- | --- | --- | --- | --- | --- |
| `validate_credentials` | Implemented | `GET /api/system` | none | `success` boolean | invalid credentials, permission denied, API unavailable |
| `search_pages` | Implemented | `GET /api/search` | `query` | page results | invalid credentials, API unavailable |
| `get_page` | Implemented | `GET /api/pages/{id}` | `page_id` | page content and metadata | page not found, invalid response |
| `create_page` | Implemented | `POST /api/pages` | title, markdown, book/chapter, tags | created page metadata | book not found, chapter not found, permission denied |
| `update_page` | Implemented | `PUT /api/pages/{id}` | page_id, title, markdown, tags | updated page metadata | page not found, permission denied |
| `publish_page` | Implemented | `GET + POST/PUT /api/pages` | page_id or match fields, content, location | create/update result | invalid match target, page not found |
| `list_books` | Implemented | `GET /api/books` | `count` and `offset` optional | books list with `count` and `total` | invalid credentials, API unavailable |
| `list_chapters` | Implemented | `GET /api/chapters` | `book_id`, `count`, and `offset` optional | chapters list with `count` and `total` | book not found, API unavailable |

## Notes

- The BookStack API uses `Authorization: Token <token_id>:<token_secret>`.
- The implemented tools already normalize response fields into Dify-friendly JSON output.
- `list_books` and `list_chapters` are implemented Phase 1 support tools before Datasource work begins.
