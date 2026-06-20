# BookStack

BookStack is a Dify plugin for publishing, reading, and syncing BookStack pages.

This repository is in active development. The current goal is to stabilize the BookStack Tool plugin MVP, document the architecture, and keep the implementation and docs aligned as Phase 1 tools land.

## Why BookStack + Dify

- Dify handles AI workflow orchestration, approvals, and agent execution.
- BookStack stores formal source documentation in a structured, open-source knowledge base.
- Together they support a documentation pipeline from draft generation to published source docs.

## Features

- Tool plugin for BookStack read/write operations.
- Credential-based access through Dify plugin configuration.
- Clear roadmap for future Datasource support.
- Documented API mapping and implementation boundaries.

## Supported Tools

Current implemented Phase 1 tool set:

- `validate_credentials`
- `search_pages`
- `get_page`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `list_chapters`

- All tools listed above are implemented in the current repository.
- Later enhancement tools and Datasource support remain planned work.

## Installation

This plugin follows the current Dify plugin structure described in the official documentation.

1. Install the Dify plugin CLI if you want to package or debug locally.
2. Configure your BookStack credentials in the Dify plugin UI.
3. Package the plugin into a `.difypkg` file and import it into a Dify environment for local validation.
4. See `docs/DEVELOPMENT.md` and `docs/MARKETPLACE.md` for version-sensitive CLI, packaging, and import guidance.

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

See `docs/examples/workflow-publish-page.md` for an example publish flow built around the implemented `publish_page` tool.

## Development Status

Current status: active development.

The repository currently contains the project skeleton, design notes, issue breakdown, the shared client, and the implemented Phase 1 BookStack tools. Later enhancement tools and Datasource work remain planned.

## Roadmap

See `docs/ROADMAP.md` for the phase-by-phase plan.

## License

MIT. See `LICENSE`.
