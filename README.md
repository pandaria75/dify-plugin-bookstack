# BookStack Plugin for Dify

BookStack Plugin for Dify connects Dify workflows and agents to self-hosted BookStack knowledge bases. Dify handles AI content generation, approval, and orchestration; BookStack stores the published documentation as a source of truth. This plugin bridges the two, enabling BookStack content lookup, search, export, non-destructive CRUD support, publishing, and related support flows from within Dify AI applications.

## Current implemented features

Implemented Dify Tool plugin features:

- `validate_credentials`
- `search_pages`
- `search_content`
- `get_page`
- `export_page_markdown`
- `create_page`
- `update_page`
- `publish_page`
- `list_books`
- `find_books`
- `get_book`
- `create_book`
- `update_book`
- `list_chapters`
- `find_chapters`
- `get_chapter`
- `create_chapter`
- `update_chapter`
- `list_shelves`
- `find_shelves`
- `get_shelf`
- `create_shelf`
- `update_shelf`
- `list_pages`
- `find_pages`
- `list_tag_names`
- `list_tag_values`

Current tool-surface notes:

- No delete or archive tools are implemented.
- Tag support in this slice is discovery-only via `list_tag_names` and `list_tag_values`.
- Tool plugin remains the primary path; Datasource work is separate and still broader follow-up scope.

Current repository direction:

- Tool plugin first
- A separate Datasource package track exists in this repository, but it is not the primary Marketplace-facing path
- Broader Datasource work remains planned

## Setup

1. Build or obtain the plugin package from this repository.
2. Import it into a Dify environment that supports plugin installation.
3. Open the BookStack provider settings in Dify.
4. Enter your BookStack `base_url`, `token_id`, and `token_secret` in the Dify UI.

See the consolidated guides:

- [English usage guide](docs/user/en/usage.md)
- [Chinese usage guide](docs/user/zh/usage.md)

## Usage

Recommended first step:

1. Save provider credentials.
2. Run `validate_credentials`.
3. Confirm the provider can reach the target BookStack instance.
4. Use the implemented search, lookup, export, listing, tag-discovery, and non-delete create/update tools as needed, and refer to the linked user docs for details.

More information is covered in the usage guides above.

## Privacy

The plugin uses credentials provided by the user and connects only to the configured BookStack instance through the Dify runtime. Privacy and credential handling guidance is covered in the usage guides and [PRIVACY.md](PRIVACY.md).

## Repository and support

- Repository: <https://github.com/pandaria75/dify-plugin-bookstack>
- Issues / support: <https://github.com/pandaria75/dify-plugin-bookstack/issues>
- Architecture intent: [docs/target/architecture-intent.md](docs/target/architecture-intent.md)

## License

MIT. See [LICENSE](LICENSE).
