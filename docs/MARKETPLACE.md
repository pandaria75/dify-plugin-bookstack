# Marketplace Guide

## Current Goal

The long-term goal is to make this plugin eligible for Dify Marketplace submission once the MVP is stable.

## Required Assets

- `manifest.yaml`
- `README.md`
- `PRIVACY.md`
- `_assets/icon.svg`

## Packaging Flow

1. Install the current Dify plugin CLI using the official Dify documentation.
2. Verify the available plugin packaging subcommands with `dify --help` and `dify plugin --help`.
3. Validate the repository shape locally before packaging.
4. Package the repository into a single `.difypkg` file.
5. Import the package into a Dify environment.
6. Run a narrow provider and tool smoke check before any release flow.

## Local Packaging Checklist

Before running the packaging command, confirm:

- `manifest.yaml` exists and still declares `plugin_type: tool`.
- `manifest.yaml` points to `provider/bookstack.yaml`.
- `_assets/icon.svg` exists.
- `provider/bookstack.yaml` still references repository-relative tool YAML files.
- `provider/bookstack.yaml` still references `provider/bookstack.py` through `extra.python.source`.
- `README.md` remains English-only.
- `PRIVACY.md` remains present.

## Local Package Command

Use the repository root as the working directory.

Current expected command shape:

```bash
dify plugin package
```

Because CLI syntax may change, treat this as a current working assumption rather than a pinned contract. If the installed CLI reports a different packaging syntax, prefer the CLI help output and update the repository docs when that newer syntax is confirmed.

Expected output:

- a generated `.difypkg` artifact for local import and release testing

## Local Import And Verification

After packaging:

1. Open a Dify environment that supports plugin import.
2. Import the generated `.difypkg`.
3. Confirm the BookStack plugin appears in the plugin list.
4. Configure provider credentials through the Dify UI only.
5. Run the smallest safe checks first.

Recommended minimum validation order:

1. Import succeeds without package-structure errors.
2. Provider form renders `base_url`, `token_id`, `token_secret`, and the optional defaults.
3. `validate_credentials` returns success for a known-good non-production BookStack target.
4. `list_books` returns accessible books.
5. `list_chapters` returns chapter data, optionally filtered by `book_id`.

Optional write-path checks for a safe test destination:

1. `create_page`
2. `update_page`
3. `publish_page`

## Current Status Notes

- Local packaging and import instructions now exist in this repository.
- A successful local Dify package smoke test has not yet been captured as evidence in the repository.
- Marketplace requirements may still change and should be revalidated before any public submission.

## GitHub Release Flow

1. Tag a release.
2. Attach the `.difypkg` artifact.
3. Document the version and changelog.

## Marketplace PR Flow

1. Review the current Marketplace submission requirements.
2. Ensure the README is English-only.
3. Ensure privacy disclosures are complete.
4. Ensure the packaged plugin can be imported and minimally exercised in a real Dify environment.
5. Prepare a PR to the Dify plugins repository only when the plugin is stable enough.
