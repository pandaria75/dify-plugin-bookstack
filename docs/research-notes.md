# Research Notes

These notes capture the repository baseline assumptions for issue `#002`. Re-check the official Dify and BookStack documentation before packaging or Marketplace submission because both plugin schemas and API details may change over time.

## Dify Plugin Structure

Current official documentation indicates that a Tool plugin should be organized around a provider YAML file and one or more tool YAML files, with Python source files referenced through `extra.python.source`.

The Marketplace documentation also requires `manifest.yaml`, `README.md`, `PRIVACY.md`, and `_assets/`.

Repository-local assumption confirmed against `dify_plugin` 0.9.1: plugin YAML references and `extra.python.source` values use repository-relative paths such as `provider/bookstack.yaml`, `tools/validate_credentials.yaml`, `provider/bookstack.py`, and `tools/validate_credentials.py`, not machine-specific filesystem paths or leading-slash paths.

## Dify CLI Status

The local environment did not have the `dify` CLI installed, so this repository was initialized manually instead of via scaffold generation.

For packaging guidance, this repository currently treats `dify plugin package` as the expected command shape, but that assumption remains version-sensitive and should be verified with the installed CLI help output before release or automation work.

Recommended local verification sequence:

```bash
dify --help
dify plugin --help
```

If the installed CLI exposes a different packaging command, the docs should be updated to match the verified command rather than keeping stale syntax.

## Datasource Findings

- Local task evidence for `#025` supports a separate Datasource package layout instead of assuming Tool + Datasource coexist in one package.
- The current repository implementation uses `bookstack_datasource/` as that separate package and keeps the root plugin focused on Tool behavior.
- The Datasource package now implements three read-only scopes: one page by `page_id`, pages under one chapter by `chapter_id`, and pages under one book by `book_id`.
- Real Dify daemon source-root import and local real-SDK import checks pass for this Datasource package after aligning SDK imports and package-local `__init__.py` files.
- Required automated regression for `#026` / `#027` / `#028` passed on 2026-06-22: deterministic client sync check, `python3 -m unittest discover -s tests -p 'test_*.py'` (99 tests, 1 skipped), and `python3 -m compileall bookstack_datasource scripts tests`.
- Full Dify UI login and Datasource plugin installation previously passed after using a valid login email and temporarily disabling `FORCE_VERIFYING_SIGNATURE` in the local Docker Dify environment.
- Live BookStack credential validation and `_get_pages` / `_get_content` live page smoke previously passed in the local Docker-backed environment using temporary BookStack test content that is cleaned up after validation.
- Local Docker services for Dify and BookStack are present in the current environment, BookStack `/api/system` responds successfully with configured credentials, the local Dify base URL and unauthenticated `system-features` endpoint responds successfully, the Datasource package repackages successfully as `dist/bookstack_datasource-0.0.1.difypkg`, and browser automation can sign in to the local Dify console when given a valid login email.
- With a valid Dify login email and browser automation, the local Dify console accepted a temporary local signature-relaxation workflow for validation: after disabling `FORCE_VERIFYING_SIGNATURE`, uploading the refreshed datasource package through `/console/api/workspaces/current/plugin/upload/pkg` and confirming installation succeeded.
- After installation, Dify's authenticated datasource-plugins API reports all three installed datasource entries: `bookstack_page`, `bookstack_chapter`, and `bookstack_book`.
- The installed runtime API also preserves the expanded nullable metadata fields and list-form `tags` schema in its datasource declarations.
- Local signature enforcement was restored after the validation attempt, and the expanded datasource declarations remain visible in the installed runtime.
- Remaining installed-runtime follow-up: credential authorization plus real content retrieval smoke for Page/Chapter/Book has not yet been completed from within Dify.
- The Datasource package appears in the Dify Plugins UI as `BookStack 数据源` / `bookstack_datasource` after installation.
- The Datasource package keeps its own `bookstack_client.py` because separate-package runtime import paths cannot rely on the root plugin module layout.
- Root `bookstack_client.py` is now the canonical source, while `bookstack_datasource/bookstack_client.py` is a deterministic generated read/traversal subset for package-local runtime use.
- Drift is checked with `python3 scripts/sync_bookstack_client.py --check`, and the broader regression path remains `python3 -m unittest discover -s tests -p 'test_*.py'`.
- A shared internal wheel/package is still a possible future direction, but it was not chosen for `#031` because this repository does not yet have Python package infrastructure and Dify source-root separation is already a packaging boundary risk.
- Stable Datasource metadata now uses fixed fields for source, sync scope/source id, page/book/chapter ids, title, URL, tags, timestamps, and content format, with nullable values preserved where practical for schema stability.
- Remaining version-sensitive runtime unknowns for `#028`: whether live Dify accepts nullable YAML metadata fields exactly as declared and whether list-form `tags` stays usable in the installed Knowledge Pipeline runtime.

## BookStack API Notes

- Authentication uses `Authorization: Token <token_id>:<token_secret>`.
- The API exposes `books`, `chapters`, `pages`, `shelves`, and `search` endpoints.
- Standard list endpoints return `data` and `total`.
- Page, chapter, and book endpoints support create, read, update, and delete operations.

For this plugin, delete operations remain out of scope unless a future issue explicitly requests them.

## Version-Sensitive Unknowns

- Full Dify UI plugin import/package-load works in the local Docker environment when signature enforcement is temporarily disabled for local validation.
- The exact supported CLI installation command and packaging syntax should be re-checked against current Dify documentation before pinning any version-specific guidance.
- Marketplace packaging requirements should be revalidated before release.
- BookStack payload details for each planned tool should be confirmed while implementing that tool and covered by mocked tests once tests exist.

## Design Judgment

The project started as a Tool plugin first because the immediate use case was read/write workflow automation. Datasource support is now implemented as a separate-package Page/Chapter/Book read-only sync path, while broader runtime confidence and release-readiness still require follow-up validation.

For the current release cycle, prefer the deterministic sync/check workflow over manual mirroring: keep root `bookstack_client.py` canonical, regenerate the Datasource subset when needed, and block drift in validation. `#031` stays ahead of the broader Datasource sync work in `#026` / `#027` / `#028`, and release-readiness should wait until the planned issue sequence is complete. Avoid runtime parent-path imports because the Dify daemon resolves plugin source files relative to the imported plugin package root.
