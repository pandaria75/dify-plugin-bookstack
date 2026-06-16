# Research Notes

## Dify Plugin Structure

Current official documentation indicates that a Tool plugin should be organized around a provider YAML file and one or more tool YAML files, with Python source files referenced through `extra.python.source`.

The Marketplace documentation also requires `manifest.yaml`, `README.md`, `PRIVACY.md`, and `_assets/`.

## Dify CLI Status

The local environment did not have the `dify` CLI installed, so this repository was initialized manually instead of via scaffold generation.

## BookStack API Notes

- Authentication uses `Authorization: Token <token_id>:<token_secret>`.
- The API exposes `books`, `chapters`, `pages`, `shelves`, and `search` endpoints.
- Standard list endpoints return `data` and `total`.
- Page, chapter, and book endpoints support create, read, update, and delete operations.

## Design Judgment

The project should start as a Tool plugin first because the immediate use case is read/write workflow automation. Datasource support should be designed later after the Tool API stabilizes.
