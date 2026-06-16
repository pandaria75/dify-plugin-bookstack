# Roadmap

## Recommended Development Order

1. Phase 0: Project initialization and research.
2. Phase 1 foundation: `validate_credentials`, `BookStackClient`, and shared error handling.
3. Phase 1 core tools: `search_pages`, `get_page`, `create_page`, `update_page`.
4. Phase 1 business flow: `publish_page`.
5. Phase 1 support tools: `list_books`, `list_chapters`.
6. Phase 1 verification: unit tests and payload mapping.
7. Phase 2 enhancement tools and safer page matching.
8. Phase 3 Datasource design and implementation.
9. Phase 4 Marketplace readiness.

## Phase 0: Project Initialization and Research

- Create the repository skeleton.
- Document architecture, API mapping, and Marketplace requirements.
- Break work into issues.
- Add minimal placeholder code only.

## Phase 1: Tool Plugin MVP

- Implement `validate_credentials`.
- Implement `search_pages`.
- Implement `get_page`.
- Implement `create_page`.
- Implement `update_page`.
- Implement `publish_page`.
- Implement `list_books`.
- Implement `list_chapters`.

## Phase 2: Enhanced Tool Coverage

- Implement `list_shelves`.
- Implement `list_pages`.
- Improve tag mapping.
- Improve page matching strategies.
- Keep delete or archive operations disabled by default.

## Phase 3: Datasource Plugin

- Design the Datasource plugin.
- Support sync by Book, Chapter, and Page.
- Add metadata mapping for Knowledge Pipeline.
- Plan shelf and full-site sync later.

## Phase 4: Marketplace Readiness

- Prepare English README and privacy policy.
- Prepare icon and usage examples.
- Add packaging and release guidance.
- Validate Marketplace submission requirements.
