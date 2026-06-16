# BookStack

BookStack is a Dify plugin for publishing, reading, and syncing BookStack pages.

This repository is in early development. The current goal is to establish a stable plugin skeleton, document the architecture, and define the first implementation steps for a BookStack Tool plugin.

## Why BookStack + Dify

- Dify handles AI workflow orchestration, approvals, and agent execution.
- BookStack stores formal source documentation in a structured, open-source knowledge base.
- Together they support a documentation pipeline from draft generation to published source docs.

## Features

- Planned Tool plugin for BookStack read/write operations.
- Credential-based access through Dify plugin configuration.
- Clear roadmap for future Datasource support.
- Documented API mapping and implementation boundaries.

## Supported Tools

Planned tool set for Phase 1:

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`

Only a minimal skeleton and credential validation placeholder are implemented in this version.

## Installation

This plugin follows the current Dify plugin structure described in the official documentation.

1. Install the Dify plugin CLI if you want to package or debug locally.
2. Configure your BookStack credentials in the Dify plugin UI.
3. Run the plugin with the Dify runtime or package it into a `.difypkg` file.

## Configuration

Configure the provider with these credential fields:

- `base_url`
- `token_id`
- `token_secret`
- `default_book_id` (optional)
- `default_chapter_id` (optional)
- `timeout_seconds` (optional)
- `verify_ssl` (optional)

## Example Workflow

See `docs/examples/workflow-publish-page.md` for the intended publish flow.

## Development Status

Current status: early development.

The repository currently contains the project skeleton, design notes, issue breakdown, and a minimal client placeholder. Core BookStack tools are still planned.

## Roadmap

See `docs/ROADMAP.md` for the phase-by-phase plan.

## License

MIT. See `LICENSE`.
