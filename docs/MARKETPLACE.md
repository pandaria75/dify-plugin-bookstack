# Marketplace Guide

## Current Goal

The near-term goal is to make this plugin straightforward to package, import, and validate locally. Marketplace submission remains a later release step after the Tool plugin MVP is stable and submission requirements are rechecked.

## Current Repository Truth

- `manifest.yaml` exists and currently declares `plugin_type: tool`.
- `manifest.yaml` currently uses `_assets/icon.svg` and registers `provider/bookstack.yaml`.
- `README.md` is English-only.
- `PRIVACY.md` exists and documents the current credential and data-handling posture.
- This repository documents packaging and import guidance, but does not yet capture successful local packaging or Dify smoke-test evidence.
- Treat all CLI command examples here as version-sensitive working assumptions until confirmed against the installed Dify CLI.

## Release Checklist

Work through this checklist before preparing any release artifact or Marketplace submission.

### 1. Manifest Preflight

- Confirm `manifest.yaml` is present at the repository root.
- Confirm `type: plugin` and `plugin_type: tool` still match the repository’s current scope.
- Confirm the top-level `version` and `meta.version` are both updated for the intended release.
- Confirm `icon: _assets/icon.svg` still points at the checked-in SVG asset.
- Confirm `plugins.tools` still references `provider/bookstack.yaml`.
- Confirm `supported_dify_version` and `minimum_dify_version` still match the intended compatibility statement for the release.

### 2. README And Privacy Check

- Confirm `README.md` remains English-only.
- Confirm `README.md` describes only implemented tools and clearly marks later work as planned.
- Confirm installation guidance still points users to local packaging and import flow, not a finished Marketplace listing.
- Confirm `PRIVACY.md` still matches actual plugin behavior and does not imply data sharing beyond Dify runtime plus the configured BookStack instance.
- If Marketplace-facing behavior or disclosures changed, update `README.md` and `PRIVACY.md` together before release work continues.

### 3. Provider And Asset Check

- Confirm `_assets/icon.svg` exists and is the same asset referenced by `manifest.yaml`.
- Confirm `provider/bookstack.yaml` still uses repository-relative references for tool YAML files.
- Confirm `provider/bookstack.yaml` still points `extra.python.source` at `provider/bookstack.py`.
- Confirm provider credentials remain defined through schema fields only, without hardcoded URLs or secrets.

### 4. Version And Change Notes

- Choose the next release version before packaging.
- Update both manifest version fields together.
- Prepare short release notes that summarize implemented tools, notable fixes, and any known limits.
- Do not describe optional local validation as Marketplace certification or production evidence.

### 5. Packaging Preparation

- Work from the repository root.
- Verify the current CLI shape with `dify --help` and `dify plugin --help`.
- Confirm the repository tree still matches the current Dify plugin layout used in this repo.
- Run the lightweight repository validation steps listed below before packaging.

### 6. Package Locally

Current expected command shape:

```bash
dify plugin package
```

If the installed CLI reports different syntax, flags, or output behavior, follow the current CLI help output and then update this document once the newer flow is confirmed.

Expected result:

- A local `.difypkg` artifact for import testing.

### 7. Import And Smoke Check

After a package is created:

1. Open a Dify environment that supports plugin import.
2. Import the generated `.difypkg`.
3. Confirm the BookStack plugin appears in the plugin list.
4. Open the provider configuration form and verify the expected fields render.
5. Enter non-production BookStack credentials through the Dify UI only.
6. Run the smallest safe checks first.

Recommended minimum validation order:

1. Import succeeds without package-structure errors.
2. Provider form renders `base_url`, `token_id`, `token_secret`, and the optional defaults.
3. Saving test credentials succeeds or returns a documented user-facing validation error without leaking secrets.
4. `validate_credentials` succeeds against a known-good non-production BookStack target.
5. `list_books` returns accessible books.
6. `list_chapters` returns chapter data, optionally filtered by `book_id`.

Optional supplemental checks for a safe test destination:

1. `search_pages`
2. `create_page`
3. `update_page`
4. `publish_page`

Local Docker-based Dify validation is acceptable as a supplemental manual path, but it is not required for GitHub Actions and should not be described as required release evidence.

### 8. Release Artifact Flow

If packaging and import checks succeed:

1. Create or prepare the release tag using the repository’s normal release process.
2. Attach the validated `.difypkg` artifact if that is part of the chosen distribution flow.
3. Publish concise release notes with the version and scope.
4. Keep any attached artifact aligned with the manifest version used to build it.

### 9. Marketplace Submission Flow

Before opening any Marketplace submission or PR:

1. Re-read the current Marketplace submission requirements.
2. Reconfirm README, privacy, icon, and manifest accuracy.
3. Reconfirm that the packaged plugin imports successfully in a real Dify environment.
4. Reconfirm that at least the minimum smoke path has been exercised and recorded somewhere durable.
5. Prepare the Marketplace submission only when the plugin is stable enough for external consumption.

## Repository Validation Commands

These checks are repository-local and safe to run before packaging:

```bash
python3 -m unittest discover -s tests
python3 -m compileall provider tools tests
```

Optional packaging check:

```bash
dify plugin package
```

Mark the packaging check as `NOT_RUN` when the Dify CLI is not installed locally or the command shape is not yet confirmed in the current environment.

## Evidence Notes

- This repository does not currently claim a successful local Dify package build as recorded evidence.
- This repository does not currently claim a successful Dify import smoke test as recorded evidence.
- Revalidate the release flow against current Dify documentation before any public submission because Marketplace and CLI requirements may change.
