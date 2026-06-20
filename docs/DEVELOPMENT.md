# Development Guide

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

Datasource support and later enhancement tools remain planned work.

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

Current repository-specific packaging assumptions:

- `manifest.yaml` declares a Dify `tool` plugin.
- `provider/bookstack.yaml` is the registered provider entry.
- Tool and provider Python sources use repository-relative paths.

Current expected packaging command shape:

```bash
dify plugin package
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
3. Expand unit tests for client behavior, payload mapping, and packaging-adjacent checks as coverage grows.
4. Capture the first successful Dify package import and smoke-test evidence in docs.
5. Expand into Phase 2, then Phase 3, then Marketplace preparation.

## Safety Rules

- Do not hardcode BookStack endpoints.
- Do not hardcode API tokens.
- Do not log secrets.
- Keep behavior minimal until the MVP tools are stable.
