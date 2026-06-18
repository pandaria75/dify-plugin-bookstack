# Current System Map

This file records how the BookStack Dify plugin works today.

This is a current-state document, not a target architecture document. Prefer observed reality over polished theory.

It must not become a code index. List only the files, entrypoints, and flows needed to explain behavior or change risk.

## Scope

- Area or workflow: Dify Tool plugin MVP for BookStack integration.
- Why this document exists: capture the current implemented plugin shape as Phase 1 tools land.
- Last substantial verification date: 2026-06-18.
- Related rules: `AGENTS.md`, `.aiassistant/rules/00-repository-rules.md`, `.aiassistant/rules/workflow-rules.md`.

## Knowledge Status

- Facts confirmed: the repository is an active Dify Tool plugin MVP; provider credential validation and the implemented Phase 1 tools use the shared BookStack HTTP client.
- Inferences needing confirmation: Dify runtime behavior for packaging and invocation should be checked against a real Dify plugin runtime before release.
- Unknowns or missing evidence: there is no automated test suite or CI entrypoint in the repository yet.

## Entrypoints

- Fact:
  - `manifest.yaml` declares the plugin as a Dify `tool` plugin and points Dify to `/provider/bookstack.yaml`.
  - `provider/bookstack.yaml` defines provider identity, credential schema, tool list, and Python provider source.
  - `provider/bookstack.py` validates configured provider credentials through `BookStackClient`.
  - `tools/validate_credentials.yaml` and `tools/validate_credentials.py` expose the credential-validation tool.
  - `tools/search_pages.yaml` and `tools/search_pages.py` expose page search.
  - `tools/get_page.yaml` and `tools/get_page.py` expose page reads.
  - `tools/create_page.yaml` and `tools/create_page.py` expose page creation.
  - `tools/update_page.yaml` and `tools/update_page.py` expose page updates.
  - `tools/publish_page.yaml` and `tools/publish_page.py` expose create-or-update publishing.
- Inference:
  - Dify packaging and runtime loading should follow the standard plugin layout already present in this repository.
- Unknown:
  - Exact Dify runtime lifecycle details have not been verified in this repository with a live package run.

## Main Call Paths

1. Fact: Dify provider credential validation -> `BookStackProvider._validate_credentials` -> `BookStackClient.from_credentials` -> `BookStackClient.validate_credentials` -> `GET /api/system`.
2. Fact: `validate_credentials` tool invocation -> runtime credentials -> `BookStackClient.validate_credentials` -> JSON success message or text error message.
3. Fact: `search_pages`, `get_page`, `create_page`, `update_page`, and `publish_page` tool invocations use `BookStackClient` for URL normalization, auth, timeout, SSL verification, and user-facing error mapping.
4. Unknown: package-level behavior after installation into Dify has not been smoke-tested here.

## Related Files And Areas

Keep this selective. Include only the files or directories that matter for understanding behavior or making safe changes.

- Fact:
  - `manifest.yaml` - plugin metadata and provider registration.
  - `provider/bookstack.yaml` - provider credentials and tool registration contract.
  - `provider/bookstack.py` - provider credential validation entrypoint.
  - `tools/validate_credentials.yaml` and `tools/validate_credentials.py` - only implemented tool contract and source.
  - `bookstack_client.py` - shared BookStack HTTP wrapper and error mapping.
  - `docs/ROADMAP.md`, `docs/DEVELOPMENT.md`, and `docs/ISSUES.md` - implementation order and current planned-vs-implemented boundary.
- Inference:
  - `docs/research-notes.md` should remain the place for version-sensitive Dify or BookStack behavior when such research is added.
- Unknown:
  - Test files, packaging commands, and CI configuration are not present yet.

## Implicit Rules And Constraints

Capture rules that appear to shape behavior even if they are not yet formalized elsewhere.

- Fact:
  - Credentials are configured through the Dify provider schema and should not be hardcoded in code, docs examples, or tests.
  - Python source references and plugin YAML references use repository-relative paths such as `provider/bookstack.py`, `tools/validate_credentials.py`, `provider/bookstack.yaml`, and `tools/validate_credentials.yaml`, matching `dify_plugin` 0.9.x local loader behavior.
  - `_assets/icon.svg` is the plugin icon path from `manifest.yaml`.
  - Keep only `list_books` and `list_chapters` described as planned Phase 1 tools.
  - `BookStackClient` is the shared integration seam for BookStack API requests and error mapping.
- Inference:
  - Future tools should add YAML contracts before Python source and tests, matching the repository working style.
- Unknown:
  - Marketplace packaging constraints still need validation against a real Dify plugin package.

## High-Risk Areas

- Credential handling and auth headers: mistakes can leak `token_secret` or make validation fail with misleading errors.
- BookStack API error mapping: user-facing contract terms are documented and should remain stable as new tools are added.
- Implemented read/write tools: `create_page`, `update_page`, and `publish_page` introduce side effects and need stronger validation than credential checks.
- Dify plugin YAML contracts: wrong source paths, credential names, or tool registrations can break runtime loading even when Python code imports locally.

## Safe-Change Advice

- Start from these entrypoints or seams: provider YAML, tool YAML, and `BookStackClient` before changing runtime behavior.
- Change these areas together when relevant: a new tool should update its YAML contract, Python source, docs/roadmap status, and tests when tests exist.
- Re-check these behaviors after changes: credential field names, `/api` URL prefixing, auth header construction, timeout/SSL handling, and documented error messages.
- Prefer these low-blast-radius approaches first: add one tool at a time and keep shared client changes minimal.
- Escalate or pause when these unknowns remain unresolved: Dify runtime packaging behavior, BookStack API payload shape, or Marketplace readiness requirements.

## Open Questions

- What exact local command should become the default validation command once tests are added?
- Which Dify plugin runtime version should be used for the first package smoke test?
- What normalized response shape should each Phase 1 BookStack tool return?

## Target-State Contrast (Optional)

- Related target doc: `docs/target/architecture-intent.md`.
- Why current state differs from target: the repository now has the core Tool plugin MVP; support tools, later enhancement work, and the Datasource direction remain planned work.

## Maintenance Notes

- Update this file when the current behavior, risks, or key paths are clarified.
- Move desired-future design into `docs/target/`, not into this file.
