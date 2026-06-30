# Current System Map

This file records how the BookStack Dify plugin works today.

This is a current-state document, not a target architecture document. Prefer observed reality over polished theory.

It must not become a code index. List only the files, entrypoints, and flows needed to explain behavior or change risk.

## Scope

- Area or workflow: Dify Tool plugin plus separate Datasource package for BookStack integration.
- Why this document exists: capture the current implemented plugin and Datasource shape.
- Last substantial verification date: 2026-06-30. Tool-surface sync updated after issue #44 export implementation and issues #45-#48 planning-only evaluation capture.
- Related rules: `AGENTS.md`, `.aiassistant/rules/00-repository-rules.md`, `.aiassistant/rules/workflow-rules.md`.

## Knowledge Status

- Fact: the repository is an active Dify Tool plugin plus a separate BookStack Datasource package; provider credential validation and the implemented tool surface use the shared BookStack HTTP client. The current tool plugin includes read, search, lookup, export, publish, tag-discovery, and non-delete CRUD helpers such as `get_book`, `create_book`, `update_book`, `get_chapter`, `create_chapter`, `update_chapter`, `get_shelf`, `create_shelf`, `update_shelf`, `list_tag_names`, `list_tag_values`, `export_chapter_markdown`, and `export_book_markdown` in addition to the earlier search/find/list/page tools.
- Fact: the separate `bookstack_datasource/` package now implements Page, Chapter, and Book read-only sync scopes that emit page-level records with stable metadata fields.
- Inferences needing confirmation: installed Dify runtime behavior for nullable Datasource metadata fields and list-form `tags` should still be checked against a real plugin runtime before release.
- Unknowns or missing evidence: expanded installed Dify Page/Chapter/Book Datasource content smoke has not yet been captured here. Browser automation can sign in to the Dify console, and the installed runtime now exposes Page/Chapter/Book datasource declarations, but credential authorization plus content retrieval checks inside Dify remain outstanding.

## Entrypoints

- Fact:
  - `manifest.yaml` declares the plugin as a Dify `tool` plugin and points Dify to `/provider/bookstack.yaml`.
  - `provider/bookstack.yaml` defines provider identity, credential schema, tool list, and Python provider source.
  - `provider/bookstack.py` validates configured provider credentials through `BookStackClient`.
  - `tools/validate_credentials.yaml` and `tools/validate_credentials.py` expose the credential-validation tool.
  - `tools/search_pages.yaml` and `tools/search_pages.py` expose page search.
  - `tools/search_content.yaml` and `tools/search_content.py` expose broader global search with type filtering.
  - `tools/get_page.yaml` and `tools/get_page.py` expose page reads.
  - `tools/export_page_markdown.yaml` and `tools/export_page_markdown.py` expose page Markdown export.
  - `tools/export_chapter_markdown.yaml` and `tools/export_chapter_markdown.py` expose chapter Markdown export with aggregate `markdown` plus structured per-page `pages` output.
  - `tools/export_book_markdown.yaml` and `tools/export_book_markdown.py` expose book Markdown export with aggregate `markdown` plus structured per-page `pages` output.
  - `tools/create_page.yaml` and `tools/create_page.py` expose page creation.
  - `tools/update_page.yaml` and `tools/update_page.py` expose page updates.
  - `tools/publish_page.yaml` and `tools/publish_page.py` expose create-or-update publishing.
  - `tools/list_books.yaml` and `tools/list_books.py` expose book listing.
  - `tools/find_books.yaml` and `tools/find_books.py` expose structured book lookup by name.
  - `tools/get_book.yaml` and `tools/get_book.py` expose book reads by ID.
  - `tools/create_book.yaml` and `tools/create_book.py` expose book creation.
  - `tools/update_book.yaml` and `tools/update_book.py` expose book updates.
  - `tools/list_chapters.yaml` and `tools/list_chapters.py` expose chapter listing with optional book filtering.
  - `tools/find_chapters.yaml` and `tools/find_chapters.py` expose structured chapter lookup by name with optional book scoping.
  - `tools/get_chapter.yaml` and `tools/get_chapter.py` expose chapter reads by ID.
  - `tools/create_chapter.yaml` and `tools/create_chapter.py` expose chapter creation.
  - `tools/update_chapter.yaml` and `tools/update_chapter.py` expose chapter updates.
  - `tools/list_shelves.yaml` and `tools/list_shelves.py` expose shelf listing.
  - `tools/find_shelves.yaml` and `tools/find_shelves.py` expose structured shelf lookup by name.
  - `tools/get_shelf.yaml` and `tools/get_shelf.py` expose shelf reads by ID.
  - `tools/create_shelf.yaml` and `tools/create_shelf.py` expose shelf creation.
  - `tools/update_shelf.yaml` and `tools/update_shelf.py` expose shelf updates.
  - `tools/list_pages.yaml` and `tools/list_pages.py` expose page listing with `count`/`offset` pagination plus optional `book_id` / `chapter_id` filtering.
  - `tools/find_pages.yaml` and `tools/find_pages.py` expose structured page lookup by name with optional `book_id` / `chapter_id` scoping.
  - `tools/list_tag_names.yaml` and `tools/list_tag_names.py` expose discovery-only tag-name listing.
  - `tools/list_tag_values.yaml` and `tools/list_tag_values.py` expose discovery-only tag-value listing for a provided tag name.
  - `bookstack_datasource/manifest.yaml` declares the separate Datasource package.
  - `bookstack_datasource/provider/bookstack_datasource.yaml` registers the Page, Chapter, and Book Datasource entries.
  - `bookstack_datasource/datasources/bookstack_page.py`, `bookstack_datasource/datasources/bookstack_chapter.py`, and `bookstack_datasource/datasources/bookstack_book.py` expose the three read-only Datasource scopes.
- Inference:
  - Dify packaging and runtime loading should follow the standard plugin layout already present in this repository.
- Unknown:
  - Exact Dify runtime lifecycle details for the expanded Datasource scopes have not been reverified in this repository with a live installed package run.

## Main Call Paths

1. Fact: Dify provider credential validation -> `BookStackProvider._validate_credentials` -> `BookStackClient.from_credentials` -> `BookStackClient.validate_credentials` -> `GET /api/system`.
2. Fact: `validate_credentials` tool invocation -> runtime credentials -> `BookStackClient.validate_credentials` -> JSON success message or text error message.
3. Fact: `search_pages`, `search_content`, `get_page`, `export_page_markdown`, `export_chapter_markdown`, `export_book_markdown`, `create_page`, `update_page`, `publish_page`, `list_books`, `find_books`, `get_book`, `create_book`, `update_book`, `list_chapters`, `find_chapters`, `get_chapter`, `create_chapter`, `update_chapter`, `list_shelves`, `find_shelves`, `get_shelf`, `create_shelf`, `update_shelf`, `list_pages`, `find_pages`, `list_tag_names`, and `list_tag_values` tool invocations use `BookStackClient` for URL normalization, auth, timeout, SSL verification, and user-facing error mapping.
4. Fact: Datasource Page/Chapter/Book sync uses the deterministic generated `bookstack_datasource/bookstack_client.py` subset, which in turn mirrors approved canonical root-client read/traversal behavior.
5. Fact: automated validation evidence is mixed by date. On 2026-06-22, `python3 scripts/sync_bookstack_client.py --check`, `python3 -m unittest discover -s tests -p 'test_*.py'` (99 tests, 1 skipped at that time), and `python3 -m compileall bookstack_datasource scripts tests` passed. On 2026-06-29 through 2026-06-30, targeted unit suites for the issues #38-#41 slices passed: `tests.test_bookstack_client` (29, later 42, tests across S2/S4), `tests.test_get_book tests.test_create_book tests.test_update_book` (13 tests), `tests.test_get_chapter tests.test_create_chapter tests.test_update_chapter tests.test_bookstack_client` (42 tests), `tests.test_get_shelf tests.test_create_shelf tests.test_update_shelf` (15 tests), `tests.test_list_tag_names tests.test_list_tag_values` (9 tests), and issue #44 export suites `tests.test_export_page_markdown tests.test_export_chapter_markdown tests.test_export_book_markdown` (19 tests). Full discover still remains blocked by a pre-existing `ModuleNotFoundError: No module named 'dify_plugin'` in `tests/test_tool_output_payloads.py`.
6. Fact: `dify plugin package bookstack_datasource --output_path dist/bookstack_datasource-0.0.1.difypkg` succeeds in the current environment.
7. Fact: Docker services for local Dify and BookStack are running in the current environment, BookStack `/api/system` responds with configured credentials, and Dify base plus unauthenticated `system-features` endpoint reachability is confirmed.
8. Unknown: expanded package-level behavior after installation into Dify has not been re-smoke-tested here for Page/Chapter/Book scopes because the sign-in form requires an email-format login and the current `.env.local` Dify username value does not satisfy that requirement.

## Related Files And Areas

Keep this selective. Include only the files or directories that matter for understanding behavior or making safe changes.

- Fact:
  - `manifest.yaml` - plugin metadata and provider registration.
  - `provider/bookstack.yaml` - provider credentials and tool registration contract.
  - `provider/bookstack.py` - provider credential validation entrypoint.
  - `tools/validate_credentials.yaml` and `tools/validate_credentials.py` - credential validation tool contract and source.
  - `tools/search_pages.yaml` and `tools/search_pages.py` - page search tool contract and source.
  - `tools/search_content.yaml` and `tools/search_content.py` - broader global search tool contract and source.
  - `tools/get_page.yaml` and `tools/get_page.py` - page read tool contract and source.
  - `tools/export_page_markdown.yaml` and `tools/export_page_markdown.py` - page Markdown export contract and source.
  - `tools/export_chapter_markdown.yaml` and `tools/export_chapter_markdown.py` - chapter Markdown export contract and source.
  - `tools/export_book_markdown.yaml` and `tools/export_book_markdown.py` - book Markdown export contract and source.
  - `tools/create_page.yaml` and `tools/create_page.py` - page creation tool contract and source.
  - `tools/update_page.yaml` and `tools/update_page.py` - page update tool contract and source.
  - `tools/publish_page.yaml` and `tools/publish_page.py` - create-or-update publish tool contract and source.
  - `tools/list_books.yaml` and `tools/list_books.py` - book listing tool contract and source.
  - `tools/find_books.yaml` and `tools/find_books.py` - structured book lookup contract and source.
  - `tools/get_book.yaml` and `tools/get_book.py` - book read tool contract and source.
  - `tools/create_book.yaml` and `tools/create_book.py` - book create tool contract and source.
  - `tools/update_book.yaml` and `tools/update_book.py` - book update tool contract and source.
  - `tools/list_chapters.yaml` and `tools/list_chapters.py` - chapter listing tool contract and source.
  - `tools/find_chapters.yaml` and `tools/find_chapters.py` - structured chapter lookup contract and source.
  - `tools/get_chapter.yaml` and `tools/get_chapter.py` - chapter read tool contract and source.
  - `tools/create_chapter.yaml` and `tools/create_chapter.py` - chapter create tool contract and source.
  - `tools/update_chapter.yaml` and `tools/update_chapter.py` - chapter update tool contract and source.
  - `tools/list_shelves.yaml` and `tools/list_shelves.py` - shelf listing tool contract and source.
  - `tools/find_shelves.yaml` and `tools/find_shelves.py` - structured shelf lookup contract and source.
  - `tools/get_shelf.yaml` and `tools/get_shelf.py` - shelf read tool contract and source.
  - `tools/create_shelf.yaml` and `tools/create_shelf.py` - shelf create tool contract and source.
  - `tools/update_shelf.yaml` and `tools/update_shelf.py` - shelf update tool contract and source.
  - `tools/list_pages.yaml` and `tools/list_pages.py` - page listing tool contract and source.
  - `tools/find_pages.yaml` and `tools/find_pages.py` - structured page lookup contract and source.
  - `tools/list_tag_names.yaml` and `tools/list_tag_names.py` - discovery-only tag-name listing contract and source.
  - `tools/list_tag_values.yaml` and `tools/list_tag_values.py` - discovery-only tag-value listing contract and source.
  - `bookstack_client.py` - shared BookStack HTTP wrapper and error mapping.
  - `bookstack_datasource/bookstack_client.py` - generated Datasource-local read/traversal client subset.
  - `bookstack_datasource/datasources/` - Datasource scope runtimes and metadata shaping.
  - `docs/ROADMAP.md`, `docs/DEVELOPMENT.md`, and `docs/ISSUES.md` - implementation order and current planned-vs-implemented boundary.
- Inference:
  - `docs/research-notes.md` should remain the place for version-sensitive Dify or BookStack behavior when such research is added.
- Unknown:
- Packaging commands are documented and the Datasource package repackages successfully, but no repository-captured live installed Dify package smoke-test evidence exists yet for the expanded Page/Chapter/Book Datasource scopes because automated sign-in cannot complete with the current Dify credential shape.

## Implicit Rules And Constraints

Capture rules that appear to shape behavior even if they are not yet formalized elsewhere.

- Fact:
  - Credentials are configured through the Dify provider schema and should not be hardcoded in code, docs examples, or tests.
  - Python source references and plugin YAML references use repository-relative paths such as `provider/bookstack.py`, `tools/validate_credentials.py`, `provider/bookstack.yaml`, and `tools/validate_credentials.yaml`, matching `dify_plugin` 0.9.x local loader behavior.
  - `_assets/icon.svg` is the plugin icon path from `manifest.yaml`.
  - The current provider tool list includes `validate_credentials`, `search_pages`, `search_content`, `get_page`, `export_page_markdown`, `export_chapter_markdown`, `export_book_markdown`, `create_page`, `update_page`, `publish_page`, `list_books`, `find_books`, `get_book`, `create_book`, `update_book`, `list_chapters`, `find_chapters`, `get_chapter`, `create_chapter`, `update_chapter`, `list_shelves`, `find_shelves`, `get_shelf`, `create_shelf`, `update_shelf`, `list_pages`, `find_pages`, `list_tag_names`, and `list_tag_values`.
  - `export_chapter_markdown` and `export_book_markdown` return aggregate `markdown` plus structured page-level `pages` output, while preserving documented user-facing error terms.
  - No delete or archive tools are implemented in the current tool surface.
  - `list_tag_names` and `list_tag_values` are discovery-only and do not mutate tags.
  - `search_pages` remains the page-focused search path while `search_content` adds broader global search.
  - `find_books`, `find_chapters`, `find_pages`, and `find_shelves` are the structured lookup tools for exact or like-style name matching.
  - `list_pages` supports optional `book_id` and `chapter_id` filtering.
  - `publish_page` supports safe matching by `page_id`, `doc_id` tag, normalized path, then exact title fallback.
  - Tag inputs normalize into BookStack tag objects with `name` and `value` fields; structured tag input avoids delimiter ambiguity.
  - `BookStackClient` is the shared integration seam for BookStack API requests and error mapping.
  - The separate Datasource package emits stable metadata fields across Page/Chapter/Book sync scopes and preserves nullable fields where practical.
- Inference:
  - Future tools should add YAML contracts before Python source and tests, matching the repository working style.
- Unknown:
  - Live Dify runtime acceptance of nullable metadata fields and list-form `tags` still needs validation against a real installed Datasource package.

## High-Risk Areas

- Credential handling and auth headers: mistakes can leak `token_secret` or make validation fail with misleading errors.
- BookStack API error mapping: user-facing contract terms are documented and should remain stable as new tools are added.
- Implemented read/write tools: `create_page`, `update_page`, and `publish_page` introduce side effects and need stronger validation than credential checks.
- Dify plugin YAML contracts: wrong source paths, credential names, or tool registrations can break runtime loading even when Python code imports locally.
- Datasource YAML metadata contracts: nullable field handling and list-form `tags` may behave differently in the installed Dify runtime than in mocked tests.
- Mock-based unit tests exist for the shared client and payload/input mapping, and Docker BookStack API smoke checks have confirmed the `books`, `chapters`, `shelves`, and `pages` list response shapes; these do not replace a real Dify runtime smoke test. Residual accepted test debt from issues #38-#41 includes missing some tool-level BookStackError/ShelfNotFound propagation checks, no explicit empty-name chapter update path coverage, and the known full-discover blocker from the unrelated `dify_plugin` import issue.

## Safe-Change Advice

- Start from these entrypoints or seams: provider YAML, tool YAML, and `BookStackClient` before changing runtime behavior.
- Change these areas together when relevant: a new tool should update its YAML contract, Python source, docs/roadmap status, and tests when tests exist.
- Re-check these behaviors after changes: credential field names, `/api` URL prefixing, auth header construction, timeout/SSL handling, documented error messages, tag payload shape, and publish matching priority.
- Re-check these behaviors after Datasource changes: page/chapter/book traversal, metadata null-handling, parent-context mapping, and Dify-installed rendering of metadata fields.
- Prefer these low-blast-radius approaches first: add one tool at a time and keep shared client changes minimal.
- Escalate or pause when these unknowns remain unresolved: Dify runtime packaging behavior, BookStack API payload shape, or Marketplace readiness requirements.

## Open Questions

- Which Dify plugin runtime version should be used for the first expanded Page/Chapter/Book Datasource package smoke test?
- Does the installed Knowledge Pipeline runtime accept nullable metadata fields and list-form `tags` exactly as the current YAML declares?

## Target-State Contrast (Optional)

- Related target doc: `docs/target/architecture-intent.md`.
- Why current state differs from target: the repository now has the core Tool plugin, the Phase 2 enhancement tools, and a broader Datasource implementation, but release-readiness and live runtime verification still lag behind target ambitions.

## Maintenance Notes

- Update this file when the current behavior, risks, or key paths are clarified.
- Move desired-future design into `docs/target/`, not into this file.
