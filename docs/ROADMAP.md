# Roadmap

## Recommended Development Order

1. Phase 0: Project initialization and research.
2. Phase 1 foundation: `validate_credentials`, `BookStackClient`, and shared error handling.
3. Phase 1 core tools: `search_pages`, `get_page`, `create_page`, `update_page`.
4. Phase 1 business flow: `publish_page`.
5. Phase 1 support tools: `list_books`, `list_chapters`.
6. Phase 1 verification: unit tests and payload mapping.
7. Phase 2 enhancement tools and safer page matching.
8. Phase 3 Datasource MVP and follow-up sync scopes.
9. Phase 4 Marketplace readiness.

## Phase 0: Project Initialization and Research

- Create the repository skeleton.
- Document architecture, API mapping, and Marketplace requirements.
- Break work into issues.
- Add minimal placeholder code only.

## Phase 1: Tool Plugin MVP

- Implemented: `validate_credentials`.
- Implemented: `search_pages`.
- Implemented: `get_page`.
- Implemented: `create_page`.
- Implemented: `update_page`.
- Implemented: `publish_page`.
- Implemented: `list_books`.
- Implemented: `list_chapters`.

## Phase 2: Enhanced Tool Coverage

- Implemented: `list_shelves`.
- Implemented: `list_pages`.
- Implemented: deterministic tag mapping.
- Implemented: page matching by title, path, and doc_id.
- Keep delete or archive operations disabled by default.

## Phase 3: Datasource Plugin

- Implemented: separate `bookstack_datasource/` package skeleton for Dify Datasource.
- Implemented: Page Datasource runtime for one `page_id`.
- Implemented: Chapter Datasource runtime for one `chapter_id`, emitting page-level sync units.
- Implemented: Book Datasource runtime for one `book_id`, emitting page-level sync units with pagination safeguards.
- Implemented: stable metadata mapping for Page/Chapter/Book Datasource output, including fixed source/scope/id fields and nullable metadata preservation where practical.
- Implemented: `#031` deterministic shared-client sync/check workflow; root `bookstack_client.py` stays canonical and the Datasource copy remains a generated read/traversal subset.
- Verified on 2026-06-22 by automated regression (sync-check, unit-test discovery, and compileall), successful Datasource repackaging, successful BookStack API credentialed connectivity, successful Dify base/system-features endpoint reachability, and successful browser sign-in to the local Dify console when using a valid login email.
- Remaining: real installed Dify runtime content smoke for the expanded Datasource package still needs credential authorization plus Page/Chapter/Book retrieval checks from within Dify. The installed runtime now recognizes all three datasource scopes and their expanded metadata declarations.
- Planned later: Shelf and full-site sync scopes.

## Phase 4: Marketplace Readiness

- Start release-readiness only after the planned issue sequence is complete; current preference is to release after all tracked issues are finished.
- Keep the English README, privacy policy, manifest, and icon aligned for Marketplace readiness.
- Capture practical packaging, import, and smoke-check evidence.
- Prepare icon and usage examples suitable for release packaging.
- Revalidate current Marketplace submission requirements before any public submission.
