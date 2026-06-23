# Developer API Mapping

## Implemented Tool Endpoints

| Dify Tool | Status | BookStack API |
| --- | --- | --- |
| `validate_credentials` | Implemented | `GET /api/system` |
| `search_pages` | Implemented | `GET /api/search` |
| `get_page` | Implemented | `GET /api/pages/{id}` |
| `create_page` | Implemented | `POST /api/pages` |
| `update_page` | Implemented | `PUT /api/pages/{id}` |
| `publish_page` | Implemented | `GET + POST/PUT /api/pages` |
| `list_books` | Implemented | `GET /api/books` |
| `list_chapters` | Implemented | `GET /api/chapters` |
| `list_shelves` | Implemented | `GET /api/shelves` |
| `list_pages` | Implemented | `GET /api/pages` |

## Current Mapping Notes

- Response normalization is part of the implemented plugin behavior.
- Shared error classification is centralized in `BookStackClient`.
- `publish_page` matching enhancements by `doc_id`, path, and exact title are implemented.
- Delete operations remain out of scope.
