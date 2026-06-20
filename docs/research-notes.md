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

## BookStack API Notes

- Authentication uses `Authorization: Token <token_id>:<token_secret>`.
- The API exposes `books`, `chapters`, `pages`, `shelves`, and `search` endpoints.
- Standard list endpoints return `data` and `total`.
- Page, chapter, and book endpoints support create, read, update, and delete operations.

For this plugin, delete operations remain out of scope unless a future issue explicitly requests them.

## Version-Sensitive Unknowns

- Dify packaging and runtime loading have not been smoke-tested in this repository yet.
- The exact supported CLI installation command and packaging syntax should be re-checked against current Dify documentation before pinning any version-specific guidance.
- Marketplace packaging requirements should be revalidated before release.
- BookStack payload details for each planned tool should be confirmed while implementing that tool and covered by mocked tests once tests exist.

## Design Judgment

The project should start as a Tool plugin first because the immediate use case is read/write workflow automation. Datasource support should be designed later after the Tool API stabilizes.
