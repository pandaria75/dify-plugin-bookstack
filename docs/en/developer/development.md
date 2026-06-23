# Developer Development Guide

## Repository Shape

This repository started as a Dify Tool plugin and now also includes a separate Datasource package. The Tool plugin remains the main focus.

## Local Development Priorities

1. Keep implemented Tool features stable.
2. Keep shared client behavior centralized in `BookStackClient`.
3. Preserve planned-vs-implemented accuracy in docs.
4. Treat Datasource packaging and runtime validation as a separate package concern.

## Dify CLI Notes

The Dify plugin CLI should be treated as version-sensitive.

Recommended verification commands:

```bash
dify --help
dify plugin --help
```

## Packaging Assumptions

- `manifest.yaml` declares the root plugin as a Dify `tool` plugin.
- `provider/bookstack.yaml` is the provider entry.
- YAML and Python source references use repository-relative paths.

## Datasource Packaging Notes

- `bookstack_datasource/manifest.yaml` defines a separate Datasource package.
- Root `bookstack_client.py` is canonical.
- `bookstack_datasource/bookstack_client.py` is a deterministic generated subset.
- Use `python3 scripts/sync_bookstack_client.py` to regenerate the Datasource copy.
- Use `python3 scripts/sync_bookstack_client.py --check` to detect drift.

## Safety Rules

- Do not hardcode BookStack endpoints.
- Do not hardcode API tokens.
- Do not log secrets.
- Keep changes minimal and consistent with the Tool-first repository direction.
