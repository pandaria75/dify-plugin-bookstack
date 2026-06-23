# Development Guide

> Navigation note: the concise developer guide now lives at [`docs/en/developer/development.md`](en/developer/development.md). This legacy file is retained for deeper implementation and packaging detail.

## Local Development

This repository currently uses a manually created plugin skeleton based on the official Dify documentation.

## Current Implemented Tool Scope

The current Tool plugin MVP includes these implemented tools:

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`
- `list_shelves`
- `list_pages`

Datasource status is now split:

- The root plugin remains the implemented Tool plugin.
- A separate `bookstack_datasource/` package now contains implemented Page, Chapter, and Book Datasource entries for BookStack sync.
- Stable Datasource metadata now covers fixed `source` / `sync_scope` / `sync_source_id` fields plus BookStack page, chapter, book, URL, tags, timestamp, and content-format fields with `null` where the source payload omits values.
- Local Dify UI package upload/install validation has previously passed for the earlier Page-only Datasource package after temporarily disabling local signature enforcement, then restoring it. Release-readiness still needs a trusted/official signing path with normal signature verification enabled.
- On 2026-06-22, required automated validation for the expanded Datasource package passed: generated-client sync check, `python3 -m unittest discover -s tests -p 'test_*.py'` (99 tests, 1 skipped), and `python3 -m compileall bookstack_datasource scripts tests`.
- On 2026-06-22, additional local validation also confirmed: BookStack `/api/system` responds successfully with configured credentials, the local Dify base URL and unauthenticated `system-features` endpoint respond successfully, `dify plugin package bookstack_datasource --output_path dist/bookstack_datasource-0.0.1.difypkg` succeeds, and browser automation can sign in to the local Dify console when given a valid login email.
- Expanded Datasource installation was advanced further in the local Docker Dify environment on 2026-06-22: after temporarily disabling local signature enforcement, uploading the refreshed package through the Dify plugins UI completed successfully, and the installed-plugin datasource API now exposes `bookstack_page`, `bookstack_chapter`, and `bookstack_book` entries.
- The installed Dify datasource declaration now also preserves the expanded nullable metadata fields and list-form `tags` schema in the runtime API output.
- Local signature enforcement was then restored to its original enabled state after the validation attempt.
- Remaining live-runtime gap: credential authorization plus real Page/Chapter/Book content retrieval smoke in the installed Dify runtime still has not been completed, so end-to-end content execution against a configured BookStack datasource remains a follow-up validation item.

## Dify CLI Preparation

The Dify plugin CLI should be treated as version-sensitive. This repository does not pin a CLI version here because the local packaging command surface may evolve.

Use this approach instead of assuming a specific installer command or release number:

1. Read the current Dify plugin documentation for the CLI installation path that matches your environment.
2. Install or update the CLI using the current official method.
3. Verify that the CLI is available locally.
4. Inspect the available plugin subcommands before packaging.

Recommended verification commands:

```bash
dify --help
dify plugin --help
```

If the second command is unavailable, re-check the official Dify plugin documentation for the current CLI packaging flow before continuing.

## Local Packaging Workflow

Package from the repository root after the CLI is installed and the plugin files are in place.

Recommended preparation checklist:

1. Confirm `manifest.yaml` exists at the repository root.
2. Confirm `_assets/icon.svg` exists.
3. Confirm `provider/bookstack.yaml` is referenced by `manifest.yaml`.
4. Confirm the provider YAML still references repository-relative tool YAML and Python source paths.
5. Confirm `README.md` remains English-only and only describes implemented tools as implemented.
6. Confirm `PRIVACY.md` still matches the current credential and data-handling behavior.

Current repository-specific packaging assumptions:

- `manifest.yaml` declares a Dify `tool` plugin.
- `provider/bookstack.yaml` is the registered provider entry.
- Tool and provider Python sources use repository-relative paths.

Current Datasource packaging notes:

- `bookstack_datasource/manifest.yaml` defines a separate Datasource package because Tool + Datasource single-package coexistence remains unverified.
- `bookstack_datasource/` now supports three read-only Datasource scopes: `bookstack_page` for one `page_id`, `bookstack_chapter` for a `chapter_id`, and `bookstack_book` for a `book_id`.
- Root `bookstack_client.py` is the canonical shared client source for this repository.
- `bookstack_datasource/bookstack_client.py` is not manually mirrored anymore. It is a deterministic generated read/traversal subset used for Datasource package-local runtime isolation.
- Run `python3 scripts/sync_bookstack_client.py` to regenerate the Datasource copy after canonical client changes.
- Run `python3 scripts/sync_bookstack_client.py --check` to fail fast on drift before packaging or review.
- Relevant validation commands for the shared-client workflow are:
  - `python3 scripts/sync_bookstack_client.py --check`
  - `python3 -m unittest tests.test_bookstack_client_sync`
  - `python3 -m unittest tests.test_bookstack_client tests.test_bookstack_datasource_page`
  - `python3 -m unittest discover -s tests -p 'test_*.py'`
- This generated-copy workflow was chosen for the current release cycle instead of a shared wheel/package because the repo does not yet have internal Python package infrastructure and Dify plugin source-root separation is already a packaging boundary risk.
- SDK import and daemon source-root import checks pass for the separate Datasource package.
- The Dify plugin CLI can package the Datasource package into `dist/bookstack_datasource-0.0.1.difypkg`.
- Full Dify UI login and Datasource plugin installation previously passed for the earlier Page-only package after providing a valid login email and temporarily disabling local signature enforcement in the Docker Dify environment.
- Live BookStack credential validation and Page-only Datasource smoke previously passed in the local Docker-backed environment using temporary BookStack test content that is cleaned up after validation.
- Expanded Page/Chapter/Book live Datasource smoke remains a follow-up validation item for the current broader Datasource runtime.
- The packaged Datasource plugin appears in the Dify Plugins UI as `BookStack 数据源` / `bookstack_datasource` after installation.

Recommended longer-term client-sharing options, in preferred order:

1. Extract the shared BookStack client into a small internal Python package or wheel consumed by both the Tool plugin and Datasource package.
2. Keep the current deterministic packaging/sync step that generates the Datasource copy from the canonical root client before building the Datasource `.difypkg`.
3. Do not return to manual vendored-copy maintenance unless a future issue explicitly accepts that tradeoff again.

Avoid relying on runtime `sys.path` hacks or parent-directory imports from the Datasource package; Dify loads plugin packages from their own source root, so package-local imports are more predictable.

Current expected packaging command shape:

```bash
dify plugin package bookstack_datasource --output_path dist/bookstack_datasource-0.0.1.difypkg
```

If the CLI now requires flags, an output directory, or a different subcommand form, follow the current official CLI help output rather than this repository note.

Expected result:

- A `.difypkg` artifact is created for import into Dify.

## Local Import Into Dify

After packaging, import the generated `.difypkg` into a Dify environment.

Typical local validation flow:

1. Start a local Dify environment, including the plugin-capable runtime you use for development.
2. Open the Dify admin or plugin management UI for that environment.
3. Import the generated `.difypkg` file.
4. Confirm the plugin appears as the BookStack Tool plugin.
5. Open provider configuration and enter test credentials through the UI fields only.

Do not paste real production secrets into documentation, screenshots, commits, or shell history you plan to share.

## Local Docker Dify Validation

When using a local Docker-based Dify environment, keep the validation narrow and observable:

1. Bring up the Dify stack you normally use for plugin testing.
2. Import the `.difypkg` through the Dify UI.
3. Add provider credentials for a non-production BookStack target.
4. Confirm the provider configuration page loads without schema errors.
5. Run the smallest safe tool checks first.

Recommended minimum order:

1. `validate_credentials`
2. `list_books`
3. `list_chapters`
4. `search_pages`

Then validate write-capable tools only against a safe Book, Chapter, or test page:

1. `create_page`
2. `update_page`
3. `publish_page`

This Docker-based validation path is supplemental manual verification for packaging and import confidence. It is not required for GitHub Actions acceptance.

## Minimal Import And Usability Check

Use this as the smallest acceptable smoke check for a local package:

1. The `.difypkg` imports successfully.
2. The plugin icon, provider name, and provider credential form render correctly.
3. Saving test credentials succeeds or returns a user-facing validation error without leaking secrets.
4. `validate_credentials` succeeds against a known-good BookStack target.
5. `list_books` returns at least one normalized result when the target account has book access.

Useful follow-up checks:

- `list_chapters` works with and without `book_id` when applicable.
- `search_pages` returns normalized search results.
- `publish_page` can create or update a page in a dedicated test location.

## Recommended Next Steps

1. Keep the implemented Phase 1 core tools stable: `search_pages`, `get_page`, `create_page`, `update_page`, and `publish_page`.
2. Keep the implemented Phase 1 support tools stable: `list_books` and `list_chapters`.
3. Keep the implemented Phase 2 enhancement tools stable: `list_shelves`, `list_pages`, deterministic tag mapping, and safer `publish_page` matching.
4. Run a real Dify Datasource package install and Page/Chapter/Book smoke pass to confirm nullable metadata fields and list-form `tags` work in the live runtime.
5. Restore normal signature verification and repeat the UI package install check before treating the Datasource package as release-ready.
6. Expand unit tests for client behavior, payload mapping, and packaging-adjacent checks as coverage grows.
7. Track the low-probability edge case where a malformed page payload without an id can yield an empty `sync_source_id`.
8. Prefer release work only after the planned issue sequence is complete; this repository currently prefers releasing after all tracked issues are finished rather than treating the current Datasource package as release-ready.

## Safety Rules

- Do not hardcode BookStack endpoints.
- Do not hardcode API tokens.
- Do not log secrets.
- Keep behavior minimal until the MVP tools are stable.
