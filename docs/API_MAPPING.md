# API Mapping

This document maps planned Dify tools to BookStack API endpoints.

## Planned Phase 1 Tools

| Dify Tool | BookStack API | Input | Output | Errors |
| --- | --- | --- | --- | --- |
| `validate_credentials` | `GET /api/system` | none | `success` boolean | invalid credentials, permission denied, API unavailable |
| `search_pages` | `GET /api/search/all` | `query` | page results | invalid credentials, API unavailable |
| `get_page` | `GET /api/pages/{id}` | `page_id` | page content and metadata | page not found, invalid response |
| `create_page` | `POST /api/pages` | title, markdown, book/chapter, tags | created page metadata | book not found, chapter not found, permission denied |
| `update_page` | `PUT /api/pages/{id}` | page_id, title, markdown, tags | updated page metadata | page not found, permission denied |
| `publish_page` | `GET + POST/PUT /api/pages` | page_id or match fields, content, location | create/update result | invalid match target, page not found |
| `list_books` | `GET /api/books` | filters optional | books list | invalid credentials, API unavailable |
| `list_chapters` | `GET /api/chapters` | `book_id` optional | chapters list | book not found, API unavailable |

## Notes

- The BookStack API uses `Authorization: Token <token_id>:<token_secret>`.
- The plugin should normalize response fields into Dify-friendly JSON output.
- Tool inputs and outputs should stay stable before Datasource work begins.
