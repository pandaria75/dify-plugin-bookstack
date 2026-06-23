# Project Roadmap

## Recommended Development Order

1. Phase 0: project initialization and research.
2. Phase 1: Tool plugin MVP foundation and core tools.
3. Phase 2: enhanced Tool coverage and safer matching behavior.
4. Phase 3: separate Datasource package and follow-up sync scopes.
5. Phase 4: Marketplace readiness.

## Current Status Summary

### Phase 1: Tool plugin MVP

Implemented:

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`

### Phase 2: Enhanced Tool coverage

Implemented:

- `list_shelves`
- `list_pages`
- deterministic tag mapping
- safer `publish_page` matching by title, path, and `doc_id`

### Phase 3: Datasource package

Implemented so far:

- separate `bookstack_datasource/` package
- Page, Chapter, and Book Datasource scopes
- stable metadata mapping
- deterministic shared-client sync/check workflow

Still pending:

- broader installed-runtime content smoke in Dify
- later sync scopes such as Shelf or full-site sync

### Phase 4: Marketplace readiness

Planned:

- align Marketplace-facing docs
- keep privacy and packaging guidance current
- capture packaging, import, and smoke-check evidence before release
