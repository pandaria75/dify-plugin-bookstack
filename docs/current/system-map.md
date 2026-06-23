# Current System Map

This file records how the BookStack Dify plugin works today.

This is a current-state document, not a target architecture document. Prefer observed reality over polished theory.

It must not become a code index. List only the files, entrypoints, and flows needed to explain behavior or change risk.

## Scope

- Area or workflow: Dify Tool plugin plus separate Datasource package for BookStack integration.
- Why this document exists: capture the current implemented plugin and Datasource shape.
- Last substantial verification date: 2026-06-22. Datasource issues #026-#028 completed with automated validation.
- Related rules: `AGENTS.md`, `.aiassistant/rules/00-repository-rules.md`, `.aiassistant/rules/workflow-rules.md`.

## Knowledge Status

- Fact: the repository is an active Dify Tool plugin plus a separate BookStack Datasource package; provider credential validation and the implemented Phase 1+2 tools use the shared BookStack HTTP client. Phase 2 added `list_shelves`, `list_pages`, deterministic tag mapping, and expanded `publish_page` matching (title, path, doc_id).
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
  - `tools/get_page.yaml` and `tools/get_page.py` expose page reads.
  - `tools/create_page.yaml` and `tools/create_page.py` expose page creation.
  - `tools/update_page.yaml` and `tools/update_page.py` expose page updates.
  - `tools/publish_page.yaml` and `tools/publish_page.py` expose create-or-update publishing.
  - `tools/list_books.yaml` and `tools/list_books.py` expose book listing.
  - `tools/list_chapters.yaml` and `tools/list_chapters.py` expose chapter listing with optional book filtering.
  - `tools/list_shelves.yaml` and `tools/list_shelves.py` expose shelf listing.
  - `tools/list_pages.yaml` and `tools/list_pages.py` expose page listing with `count`/`offset` pagination.
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
3. Fact: `search_pages`, `get_page`, `create_page`, `update_page`, `publish_page`, `list_books`, `list_chapters`, `list_shelves`, and `list_pages` tool invocations use `BookStackClient` for URL normalization, auth, timeout, SSL verification, and user-facing error mapping.
4. Fact: Datasource Page/Chapter/Book sync uses the deterministic generated `bookstack_datasource/bookstack_client.py` subset, which in turn mirrors approved canonical root-client read/traversal behavior.
5. Fact: automated validation on 2026-06-22 passed `python3 scripts/sync_bookstack_client.py --check`, `python3 -m unittest discover -s tests -p 'test_*.py'` (99 tests, 1 skipped), and `python3 -m compileall bookstack_datasource scripts tests`.
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
  - `tools/get_page.yaml` and `tools/get_page.py` - page read tool contract and source.
  - `tools/create_page.yaml` and `tools/create_page.py` - page creation tool contract and source.
  - `tools/update_page.yaml` and `tools/update_page.py` - page update tool contract and source.
  - `tools/publish_page.yaml` and `tools/publish_page.py` - create-or-update publish tool contract and source.
  - `tools/list_books.yaml` and `tools/list_books.py` - book listing tool contract and source.
  - `tools/list_chapters.yaml` and `tools/list_chapters.py` - chapter listing tool contract and source.
  - `tools/list_shelves.yaml` and `tools/list_shelves.py` - shelf listing tool contract and source.
  - `tools/list_pages.yaml` and `tools/list_pages.py` - page listing tool contract and source.
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
  - Phase 1 support tools `list_books` and `list_chapters` are implemented.
  - Phase 2 enhancement tools `list_shelves` and `list_pages` are implemented.
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
- Mock-based unit tests exist for the shared client and payload/input mapping, and Docker BookStack API smoke checks have confirmed the `books`, `chapters`, `shelves`, and `pages` list response shapes; these do not replace a real Dify runtime smoke test.

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
