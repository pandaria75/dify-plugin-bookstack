# Issues

The repository keeps the issue plan in Markdown so the roadmap is always visible even before GitHub issue creation is complete.

## Recommended Issue Order

1. `#001` to `#002` for repository and research baseline.
2. `#003` to `#004` for credentials and shared client foundation.
3. `#005` to `#009` for the Phase 1 Tool MVP, ending with `publish_page`.
4. `#010` to `#011` for tests and core docs.
5. `#012` to `#019` for support tools, reliability, and Marketplace prep.
6. `#020` to `#030` for Phase 2 and Phase 3 expansion.
7. `#031` for Datasource shared-client maintenance hardening before broader sync work in `#026` / `#027` and before release-readiness work.

| ID | Title | Priority | Type | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| #001 | Initialize Dify plugin repository skeleton | P0 | Foundation | Minimal Dify plugin files, docs, and assets exist. |
| #002 | Research current Dify plugin structure and BookStack API requirements | P0 | Research | `docs/research-notes.md` records current official guidance and assumptions. |
| #003 | Add BookStack credential schema and provider validation | P0 | Provider | Credentials are configured through provider schema and validated without leaking secrets. |
| #004 | Implement BookStackClient base HTTP wrapper | P0 | Core | Client handles URL normalization, auth header, timeout, SSL, JSON parsing, and error mapping. |
| #005 | Implement search_pages tool | P0 | Tool | Tool accepts `query` and returns normalized page search results. |
| #006 | Implement get_page tool | P0 | Tool | Tool reads a page by ID and returns content plus metadata. |
| #007 | Implement create_page tool | P0 | Tool | Tool creates a page and returns `page_id`, `title`, `url`, and `action`. |
| #008 | Implement update_page tool | P0 | Tool | Tool updates a page and returns normalized update metadata. |
| #009 | Implement publish_page tool | P0 | Tool | Tool supports create-or-update publishing and returns `success`, `action`, `page_id`, `title`, and `url`. |
| #010 | Add basic unit tests for BookStackClient and payload mapping | P0 | Testing | Tests cover client behavior and payload mapping without real BookStack credentials. |
| #011 | Add README, PRIVACY, ROADMAP and architecture docs | P0 | Documentation | Core docs exist and planned features are not described as complete. |
| #012 | Implement list_books tool | P1 | Tool | Implemented: tool returns accessible books with stable metadata fields. |
| #013 | Implement list_chapters tool | P1 | Tool | Implemented: tool lists chapters, optionally filtered by `book_id`. |
| #014 | Improve error handling and user-facing error messages | P1 | Reliability | Common API failures map to documented user-facing errors. |
| #015 | Add example Dify Workflow documentation | P1 | Documentation | Example publish-page workflow documentation exists. |
| #016 | Add local packaging guide with dify plugin package | P1 | Documentation | Local packaging instructions are documented and reference Dify CLI. |
| #017 | Add CI for lint and tests | P1 | CI | Pull requests run unit tests and selected static checks. |
| #018 | Add GitHub issue templates | P1 | Repository Maintenance | Bug, feature, and question issue templates exist. |
| #019 | Add Marketplace release checklist | P1 | Documentation | Marketplace checklist covers manifest, README, privacy, icon, version, packaging, import, and release flow. |
| #020 | Implement list_shelves tool | P2 | Tool | Implemented: tool lists shelves with normalized output. |
| #021 | Implement list_pages tool | P2 | Tool | Implemented: tool lists pages with stable metadata and `count`/`offset` pagination. |
| #022 | Support tags mapping more completely | P2 | Data Mapping | Implemented: tag inputs normalize deterministically to BookStack tag objects. |
| #023 | Support page matching by title/path/custom doc_id | P2 | Tool Logic | Implemented: `publish_page` supports `page_id`, `doc_id`, `path`, and exact-title matching strategies. |
| #024 | Add Datasource plugin design document | P2 | Design | Datasource design covers sync scopes and metadata mapping. |
| #025 | Implement BookStack datasource MVP | P2 | Datasource | Implemented: a separate `bookstack_datasource/` package provides a Page-only Datasource MVP for one `page_id`, with focused mocked tests, Docker-backed live Page smoke validation, Dify CLI packaging, and local Dify UI install validation. Trusted/official signature validation remains a release-readiness follow-up. |
| #026 | Add sync range by Book | P2 | Datasource | Planned: Book-scoped sync is supported and documented. |
| #027 | Add sync range by Chapter | P2 | Datasource | Planned: Chapter-scoped sync is supported and documented. |
| #028 | Add metadata mapping for Knowledge Pipeline | P2 | Data Mapping | Knowledge metadata includes source, IDs, title, URL, tags, and timestamps beyond the current Page-only MVP mapping. |
| #029 | Prepare Marketplace submission | P2 | Release | Planned: release package and submission checklist are ready for Marketplace PR after the broader issue sequence is complete. |
| #030 | Add screenshots and sample workflows | P2 | Documentation | Screenshots and sample workflows reflect real MVP behavior. |
| #031 | Replace vendored Datasource BookStackClient with shared packaging strategy | P2 | Technical Debt | Tool plugin and Datasource package avoid manually maintained divergent client logic through the canonical root client plus deterministic sync/check workflow before broader Datasource sync or release work. |
