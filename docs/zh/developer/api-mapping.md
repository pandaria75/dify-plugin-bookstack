# 开发者 API 映射

## 已实现的 Tool 端点

| Dify Tool | 状态 | BookStack API |
| --- | --- | --- |
| `validate_credentials` | 已实现 | `GET /api/system` |
| `search_pages` | 已实现 | `GET /api/search` |
| `get_page` | 已实现 | `GET /api/pages/{id}` |
| `create_page` | 已实现 | `POST /api/pages` |
| `update_page` | 已实现 | `PUT /api/pages/{id}` |
| `publish_page` | 已实现 | `GET + POST/PUT /api/pages` |
| `list_books` | 已实现 | `GET /api/books` |
| `list_chapters` | 已实现 | `GET /api/chapters` |
| `list_shelves` | 已实现 | `GET /api/shelves` |
| `list_pages` | 已实现 | `GET /api/pages` |

## 当前映射说明

- 响应规范化属于已实现的插件行为。
- 共享错误分类集中在 `BookStackClient` 中。
- `publish_page` 通过 `doc_id`、路径与精确标题进行匹配的增强功能已实现。
- 删除操作仍然不在范围内。
